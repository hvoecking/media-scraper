Media Scraper
=============

Python script for playing all media on tagesschau.de with a single click


I always imagined how nice it would be, if I got up and only needed a single click to enjoy my news during breakfast.
Well the time has come that my dream came true.
If you want, feel free to join me :)


Installation
============

You might need to download urllib, cookielib and/or BeautifulSoup.
You can do this with easy_install and pip.

Run
===

Run this code with python3, the media-scraper-p2.py file is built for python2
- currently only tested on Linux

Download
========

Using the standard options the ammount downloaded per day will average at about 80MB to 90MB.
Ranging from 20MB up to 150MB or more.

License
=======

This program is distributed WITHOUT ANY WARRANTY!

I am happy if you want to use my code (or parts of it) in your project.
So if you do, please contact me first before publishing your code!

TODO
====
- Fix formatting of last row on downloading
- Do not touch files anymore
- Do not split up in subfolders by date anymore to avoid downloading same files multiple times
- Set track name in playlist as website title
- Download to same directory per topic (cut off numbers at the end)
- Command line options / settings file
-- Help
-- Audio/Video quality
-- Directory for download
-- Media Player
-- Download manager
-- Max age of files
- Save in default downloads folder
- Sort playlist by article > time
- Render the webpage and set it as covor image for audio files
- Buffered cmd-line output
