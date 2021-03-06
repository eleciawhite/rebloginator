
# You'll likely need to pip3 install these
import feedparser
import PyRSS2Gen
import dateutil.parser # pip3 install python-dateutil
import pytz #python timezones

# These are standard and should not need additional installs
import urllib
import json
import os
import glob
import datetime

import re

print("Content-type: text/html\n\n") # dreamhost to allow outputs

# output paths, all relative to script
CONFIG_PATH = "cfg"
RSS_OUTPUT_PATH = "rss"
TMP_OUTPUT_PATH = "tmp"

# access the Internet Archive
waybackJsonURL = 'http://web.archive.org/web/timemap/json/'
waybackWebURL = 'http://web.archive.org/web/'
TIME = 1    # where time is in the Wayback output
ENDURL = 2  # the target URL in the wayback output
CACHE_FREQUENCY_DAYS = 10 #days until you can update the cache

TIME_ZERO = datetime.datetime.min.replace(tzinfo=pytz.utc).__str__()

# 1. Read the URL on the Wayback machine http://web.archive.org/web/timemap/link/$URL
# 2. Concatenate the feeds, removing duplicates and order according to time (oldest to newest?)
# 3. Store the resultant feed. <-- MAYBE, could be a space suck
# 4. Send them to the user one post at a time

# get a list of posts in the blog, given overlapping RSS URLs from wayback
def getCompleteBlogPosts(rssLines):
    feed = []
    for line in rssLines:
        url = waybackWebURL +  line[TIME] +'/' + line[ENDURL]
        thisfeed = feedparser.parse(url)
        feed.extend(thisfeed["items"]) # combine RSS items list 

    # also get the latest posts
    thisfeed = feedparser.parse(rssLines[1][ENDURL])
    feed.extend(thisfeed["items"])
    
    #sort and remove duplicates
    sortedEntries = sorted(feed, key=lambda entry: dateutil.parser.parse(entry["published"]))
    sortedParedEntries = []
    for i in range(0,len(sortedEntries)-1):  
        if (sortedEntries[i]["published"] != sortedEntries[i+1]["published"]):
            sortedParedEntries.append(sortedEntries[i])
    sortedParedEntries.append(sortedEntries[len(sortedEntries)-1])
    return sortedParedEntries

# use the wayback machine to look up old revisions of the rss file, ideally getting 
# all or most posts by combining together wayback snapshots (momentos)
def getListOfRssLine(inputURL):
    response = urllib.request.urlopen(waybackJsonURL+inputURL)
    waybackListOfRSSCaptures = response.read()
    return waybackListOfRSSCaptures

# get a complete list of entries in the blog from an input URL of the RSS 
def getFeed(inputURL):
    waybackListOfRSSCaptures = getListOfRssLine(inputURL)
    rssLines = json.loads(waybackListOfRSSCaptures)
    feed = getCompleteBlogPosts(rssLines)
    return feed

# get the post in the ordered feed after the given data string
def postAfter(feed, dateStr):
    after = None
    date = dateutil.parser.parse(dateStr)
    for entry in feed:
        if dateutil.parser.parse(entry["published"]) > date:
            return entry
    return after


# debug: print all of the titles that are in the feed along with a count
# of how many there are
def printTitles(feed):
    for entry in feed:
        print(entry["published"] + " " + makeHappyAscii(entry["title"])) 

# output the current status of the blog: where are we and when did we last post
def writeStatus(feedname, status):
    statusFilename = os.path.join(TMP_OUTPUT_PATH, (feedname + ".json"))
    statusFile = open(statusFilename, 'w+')
    json.dump(status, statusFile)
    statusFile.close()

# read in the current status of the blog to determine if it is time to reblog
# This will also create a new status file if one does not exist
def readStatus(cfg):
    feedname = cfg["feedName"]
    statusFilename = os.path.join(TMP_OUTPUT_PATH, (feedname + ".json"))
    if os.path.isfile(statusFilename):
        statusFile = open(statusFilename, 'r')
        status = json.loads(statusFile.read())
        statusFile.close()
    else:
        print("Creating status file: " + statusFilename)
        status ={}
        status["lastRepost"] = TIME_ZERO 
        status["publishDateLastRepost"] = cfg["startDate"]
        status["RSSCached"] = False
        status["RSSCacheDate"] = TIME_ZERO 
        status["RSSCacheFile"] = cfg["feedName"] + ".rss"
        writeStatus(feedname, status)
    return status

# Read the RSS from a local cache. If the local cache does not exist, create it
# (which could take a lot of time)        
def getTheRss(cfg, status):
    haveGoodCache = False
    feedname = cfg["feedName"]
    rssUrl = cfg["url"]
    cacheFilename = os.path.join(TMP_OUTPUT_PATH, (feedname + ".rss"))
    if status["RSSCached"]: # read the cache
        cacheFile = open(cacheFilename, 'r')
        feed = json.loads(cacheFile.read())
        if (None != feed):
            haveGoodCache = True
            print("Cache is good.")

    if False == haveGoodCache:
        #read the whole feed, then cache it
        feed = getFeed(rssUrl)
        print("Creating cache.")
        cacheFile = open(cacheFilename, 'w')
        status["RSSCached"] = True
        status["RSSCacheDate"] = datetime.datetime.now(datetime.timezone.utc).__str__()
        status["RSSCacheFile"] = feedname + ".rss"
        json.dump(feed, cacheFile)

        writeStatus(feedname, status)
    cacheFile.close()
    return feed

# no more posts, next time get a new cache
def checkCacheReload(status):
    lastCacheDate = dateutil.parser.parse(status["RSSCacheDate"])
    goalCacheDate = lastCacheDate + datetime.timedelta(days = CACHE_FREQUENCY_DAYS)
    now = datetime.datetime.now(datetime.timezone.utc)
    if (goalCacheDate < now):
        print("Clearing cache for next time.")
        status["RSSCached"] = False
    return status

# Unicode is a pain and blogs can be anything but the server wants everything in ascii
# so this function replaces curly quotes with single quotes and then moves to ascii,
# ignoring unicode characters.
def makeHappyAscii(str):
    singleQuotesRemoved = re.sub(u'[\u2019]','\'',str)
    doubleQuotesRemoved = re.sub(u'[\u201c\u201d]','\"',singleQuotesRemoved)
    reEncoded = bytes(doubleQuotesRemoved, encoding='utf-8').decode("ascii", "ignore") 
    return reEncoded

# Output the new blog entry. This prepends it to the current RSS output. 
# To do that it has to read in the previous RSS entries and 
# outputting as many as the configuration file indicates. Note, if there
# are no previous entries, it will generate a new RSS.
def outputItem(cfg, outputFilename, item):
    outFilenameWithPath = os.path.join(RSS_OUTPUT_PATH, outputFilename)
    if os.path.isfile(outFilenameWithPath):
        outputFile = open(outFilenameWithPath, 'r')
        d = feedparser.parse(outputFile.read())
        outputFile.close()
        
        items = [PyRSS2Gen.RSSItem( 
                title = x.title, 
                link = x.link, 
                description = x.summary, 
                guid = x.link, 
                pubDate = dateutil.parser.parse(item["published"]))    
        for x in d.entries]
        if (len(items) > cfg["keepEntries"]): # only keep a limited number of entries
            items.pop()

        rss = PyRSS2Gen.RSS2( 
            title = d.feed.title, 
            link = d.feed.link, 
            description = d.feed.description, 
            lastBuildDate = datetime.datetime.now(), 
            items = items) 
    else:
        print("Creating output file: " + outFilenameWithPath)
        rss = PyRSS2Gen.RSS2(
            title = cfg["feedName"],
            link = cfg["url"],
            description = 'Rebloginator re-blog!',
            items = []
        )

    rss.items.insert(0, PyRSS2Gen.RSSItem(
            title = makeHappyAscii(item["title"]),
            link = item["link"],
            description = makeHappyAscii(item["summary"]),
            guid = item["link"],
            pubDate =  dateutil.parser.parse(item["published"])
            ))

    outFilenameWithPath = os.path.join(RSS_OUTPUT_PATH, outputFilename)
    outFile = open(outFilenameWithPath, 'w+')
    rss.write_xml(outFile)
    outFile.close()

# This is the start of it all, looking through the config files in the CONFIG_PATH
# Reading the related status and posting if it is time.
if __name__ == "__main__":
    # test running the data
    for cfgFilename in glob.glob(os.path.join(CONFIG_PATH, '*.json')):
        with open(cfgFilename, 'r') as cfgFile:
            print("Reading " + cfgFilename)
            cfg = json.loads(cfgFile.read())
            status = readStatus(cfg)
            lastRepost = dateutil.parser.parse(status["lastRepost"])
            goalPostTime = lastRepost + datetime.timedelta(hours = cfg["updateFrequencyInHours"])
            now = datetime.datetime.now(datetime.timezone.utc)
            if goalPostTime < now:
                feed = getTheRss(cfg, status)    
                post = postAfter(feed, status["publishDateLastRepost"])
                if post is not None:
                    status["lastRepost"] = datetime.datetime.now(datetime.timezone.utc).__str__()
                    status["publishDateLastRepost"] = post["published"]
                    printTitles([post])
                    outputItem(cfg, status["RSSCacheFile"], post)
                else: 
                    print("No more posts...")
                    status = checkCacheReload(status)
                writeStatus(cfg["feedName"], status)
            else:
                print("Not time for this to post.")
