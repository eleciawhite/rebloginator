# rebloginator
The rebloginator (re-blog-inator) is a tool to read a blog from the start instead of only the last 20 posts or instead of digging through someone's website one laborious Older buttong press at a time.

The idea is that you put in a blog RSS URL that you want to read, a date you want to start reading from, and how often you want new posts. Rebloginator will then generate a new RSS feed you can subscribe to that will be update with the parameters you specify.

## Goal ##
In its final incarnation, this script will run via cron job on a server. It will use config files for use input and (probably) temporary files to note which post was last sent and when the next one is due for each. Its output will be a series of RSS files, one for each config input. 

## The Problem ##
Each RSS feed only has the last N posts. For XKCD, that is 5. For Questionable Content, it is 400. For Squarespace-hosted blogs like Embedded.fm it is a fixed 20. There is no consistent way to get to older posts. Some URLs might take a all=true flag, Squarespace will provide 20 more items using the ofset=magicTime parameter. (The magicTime is the epoch time of the last post on the previous URL, I think.)

Anyway, blogs are meant to be read from now forward, no backsies. Defeating this has been a surprising pain.

While I believe I can use magicTime on Squarespace, I want a more generic utility, even if it means missing a few posts. I'm using the internet archive Wayback Machine to read the top level RSS feed as it is captured.

## Current status ##
Nowhere near the goal.

Given a target blog URL, the script will query the Wayback Machine, getting a JSON file of all of the captures of the blog URL. The script will then query each of those to get a list of blog entries. 

The blog entries are sorted and duplicates removed.

At this point the titles are printed out and the number of entries. This may seem unexciting but it is a step on the path to world dominating reblogination. 







A tool to read a blog from the start