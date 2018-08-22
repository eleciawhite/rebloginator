# rebloginator
The rebloginator (re-blog-inator) is a tool to read a blog from the start instead of only the last 20 posts or instead of digging through someone's website one laborious Older button press at a time.

The idea is that you put in a blog RSS URL that you want to read, a date you want to start reading from, and how often you want new posts. Rebloginator will then generate a new RSS feed you can subscribe to that will be update with the parameters you specify.

## Goal ##
In its final incarnation, this script will run via cron job on a server. It will use config files for use input and (probably) temporary files to note which post was last sent and when the next one is due for each. Its output will be a series of RSS files, one for each config input. 

## The Problem ##
Each RSS feed only has the last N posts. For XKCD, that is 5. For Questionable Content, it is 400. For Squarespace-hosted blogs like Embedded.fm it is a fixed 20. There is no consistent way to get to older posts. Some URLs might take a all=true flag, Squarespace will provide 20 more items using the ofset=magicTime parameter. (The magicTime is the epoch time of the last post on the previous URL, I think.)

Anyway, blogs are meant to be read from now forward, no backsies. Defeating this has been a surprising pain.

While I believe I can use magicTime on Squarespace, I want a more generic utility, even if it means missing a few posts. I'm using the internet archive Wayback Machine to read the top level RSS feed as it is captured.

## Current status ##
Near the goal, limited testing.

Given a target blog URL, the script will query the Wayback Machine, getting a JSON file of all of the captures of the blog URL. The script will then query each of those to get a list of blog entries. 

The blog entries are sorted and duplicates removed. The correct new-post is chosen. A certain number are kept in the output RSS file before they expire.

Essentially, it is time for the cron job and some other test blogs.

## Fails ##
This does not work on [False Knees](http://falseknees.com/334.html).

## Installing on a Server ##

Find a nice server that you have access to, this could be a Raspberry Pi or AWS. For me, it is going to be Dreamhost. I found [an explantion of setting up a server that help me get over the initial fear and hurdles]https://gist.github.com/moonmilk/8d78032debd16f31a8a9). It boiled down to a few fairly simple steps. Install [python3](https://help.dreamhost.com/hc/en-us/articles/115000702772-Installing-a-custom-version-of-Python-3), possibly create a [virtual environment](https://help.dreamhost.com/hc/en-us/articles/115000695551-Installing-and-using-virtualenv-using-Python-3). Next, you'll need to install a few libraries:

pip3 install feedparser PyRSS2Gen python-dateutil timezones

From there, you should be able to run on the server, at least enough to get an output you can try with your feed reader (or an [online one](http://www.feedbucket.com/)). Next, you'll want to set up a cron job to run rebloginator regularly.

## Skip to the End ##
If the idea sounds good but this implementation seems, well, unfinished, there is another, already existing solution:

[Backfeed](http://backfeed.strangecode.com/) bills itself as the Wayback Machine for podcast feeds. It is only through the author Quinn Comendant's comments on StackOverflow that I thought of usinig the Wayback machine myself.

I do intend to continue development on my script because mine will be open so you can run it on your own server instead of getting an access key from Quinn and filling up his server.