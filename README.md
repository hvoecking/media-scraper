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

MIT

TODO
====
- [x] Fix formatting of last row on downloading
- [x] Do not touch files anymore
- [x] Do not split up in subfolders by date anymore to avoid downloading same files multiple times
- [x] Set track name in playlist as website title
- [x] Download to same directory per topic (cut off numbers at the end)
- [x] Command line options / settings file
  - [x] Help
  - [x] Audio/Video quality
  - [x] Directory for download (default: Save in downloads folder)
  - [x] Media Player
  - [x] Download manager
  - [x] Max age of files
- [x] Sort playlist by general article topic > time
- [ ] Format code
- [x] Consistently sort video stuff before audio stuff
- [x] Quote style according to http://stackoverflow.com/questions/56011/single-quotes-vs-double-quotes-in-python
- [ ] Code style according to http://google-styleguide.googlecode.com/svn/trunk/pyguide.html#Semicolons
- [ ] Render the webpage and set it as covor image for audio files
- [ ] Buffered cmd-line output
