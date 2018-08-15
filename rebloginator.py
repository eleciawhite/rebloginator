import feedparser
from html.parser import HTMLParser
import urllib
import json
import copy
import os
import glob
import  dateutil.parser


TESTING_FIXED_CAPS = True # less wayback traffic
TIME = 1    # where time is in the Wayback output
ENDURL = 2  # the target URL in the wayback output
CONFIG_PATH = "cfg"


# 1. Read the URL on the Wayback machine http://web.archive.org/web/timemap/link/$URL
# 2. Concatenate the feeds, removing duplicates and order according to time (oldest to newest?)
# 3. Store the resultant feed. <-- MAYBE, could be a space suck
# 4. Send them to the user one post at a time
waybackJsonURL = 'http://web.archive.org/web/timemap/json/'
waybackWebURL = 'http://web.archive.org/web/'

def getListOfItems(rssLines):
    feed = []
    for line in rssLines:
        url = waybackWebURL +  line[TIME] +'/' + line[ENDURL]
        thisfeed = feedparser.parse(url)
        feed.extend(thisfeed["items"]) # combine RSS items list 

    sortedEntries = sorted(feed, key=lambda entry: dateutil.parser.parse(entry["published"]))
    sortedParedEntries = []
    for i in range(0,len(sortedEntries)-1):  
        if (sortedEntries[i]["published"] != sortedEntries[i+1]["published"]):
            sortedParedEntries.append(sortedEntries[i])
    sortedParedEntries.append(sortedEntries[len(sortedEntries)-1])
    return sortedParedEntries

def getListOfRssLine(inputURL):
    if not TESTING_FIXED_CAPS:
        response = urllib.request.urlopen(waybackJsonURL+inputURL)
        waybackListOfRSSCaptures = response.read()
    else:
        waybackListOfRSSCaptures = '[["urlkey","timestamp","original","mimetype","statuscode","digest","redirect","robotflags","length","offset","filename"], \
        ["fm,embedded)/blog?format=rss","20160303172611","http://embedded.fm:80/blog?format=RSS","application/rss+xml","200","HPD2LGQOXB5T77EW32HEKHQRTOUTBB2Y","-","-","47809","89047138","alexa20160304-26/52_51_20160303172437_crawl302.arc.gz"],\
        ["fm,embedded)/blog?format=rss","20160415235438","http://embedded.fm:80/blog/?format=rss","application/rss+xml","200","GSFAOIDOGLP345JAQSV7CIJCARO3VPZ6","-","-","62374","82777796","alexa20160416-35/52_51_20160415235357_crawl302.arc.gz"],\
        ["fm,embedded)/blog?format=rss","20160503203836","http://embedded.fm:80/blog?format=RSS","application/rss+xml","200","YKSCQC45AVIS6RX2S7NUXOLYBB34MWS3","-","-","64458","59772429","alexa20160504-31/52_52_20160503203812_crawl302.arc.gz"], \
        ["fm,embedded)/blog?format=rss","20160527112148","http://embedded.fm/blog?format=RSS","application/rss+xml","200","RUH424UU6G6AYYTZOQ4E3Y3ZTBKRNO6B","-","-","58979","239852212","WIDE-20160527111127-crawl426/WIDE-20160527111341-00139.warc.gz"]]'

    return waybackListOfRSSCaptures


def getFeed(inputURL):
    waybackListOfRSSCaptures = getListOfRssLine(inputURL)
    rssLines = json.loads(waybackListOfRSSCaptures)
    feed = getListOfItems(rssLines)
    return feed


def postsAfer(feed, dateStr):
    after = []
    date = dateutil.parser.parse(dateStr)
    for entry in feed:
        if dateutil.parser.parse(entry["published"]) > date:
            after.append(entry)
    return after



def printTitles(feed):
    count = 0
    for entry in feed:
        print(entry["published"] + " " + entry['title']) 
        count = count + 1

    print(count)

for filename in glob.glob(os.path.join(CONFIG_PATH, '*.json')):
    with open(filename, 'r') as f:
        print("Reading " + filename)
        blogInfo = json.loads(f.read())
        print(blogInfo["url"])
        feed = getFeed(blogInfo["url"])
        # get posts after startDate
        after = postsAfer(feed, blogInfo["startDate"])

        printTitles(after)

