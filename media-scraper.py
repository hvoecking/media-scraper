#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  media-scraper.py
#  
#  Copyright 2013 Heye Vöcking <heye.voecking at gmail.com>
#    
#  This program is distributed WITHOUT ANY WARRANTY!
#  I am happy if you want to use my code (or parts of it) in your 
#  project. So if you do, please contact me first before publishing
#  your code!
#  
#  


import os
import sys
from datetime import date
import re
import argparse
import urllib.request
import urllib.parse
import urllib.error
import urllib.request
import urllib.error
import urllib.parse
import http.cookiejar
from bs4 import BeautifulSoup
import const as c

# From http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
class bcolors:
    BOLD_SEQ = "\033[1m"
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''


def parse_args():
	
	# Arguments
	parser = argparse.ArgumentParser(description="Optional arguments")
							 
	parser.add_argument("-v, --video-quality",
						choices=c.VIDEO_QUALITIES.keys(),
						default='webm',
						dest='video',
					    help="There are %d different video qualities "
							 "available for download: %s" % 
							 (len(c.VIDEO_QUALITIES), 
							  str(c.VIDEO_QUALITIES)))

	parser.add_argument("-a, --audio-quality",
						choices=c.AUDIO_QUALITIES.keys(),
						default='mp3',
						dest='audio',
					    help="There are %d different audio qualities "
							 "available for download." % 
							 len(c.AUDIO_QUALITIES))
							 
	parser.add_argument("-d, --download-directory",
						dest='dir',
						default="~/Downloads",
						help="The directory to which the files should "
							 "be downloaded.")
							 
	parser.add_argument("-f, --file-age",
						dest='age',
						default=0,
						help="The maximum number of days since the "
							 "file has been published. Use 0 for "
							 "unlimited.")
							 
	parser.add_argument("-p, --player",
						dest='player',
						default="vlc",
						help="The media player which will be called "
							 "to open the generated playlist.")
							 
	parser.add_argument("-l, --playlist-format",
						dest='playlist',
						default="m3u",
						choices={"m3u"},
						help="The format of the playlist, currently "
							 "only m3u is supported")
							 
	parser.add_argument("-t, --download-tool",
						choices={'curl','wget'}
						dest='tool',
						default="curl",
						help="The command line tool used to download "
							 "the media files. Command line output "
							 "is optimized for curl.")
							 
	default_ua = ("Mozilla/5.0 (Windows; U; Windows NT 6.1; ru; "
				  "rv:1.9.2.3) Gecko/20100401 Firefox/4.0 "
				  "(.NET CLR 3.5.30729)")
	parser.add_argument("-u, --user-agent",
						dest='ua',
						default=default_ua,
						help="The user agent to be used.")
						
	parser.add_argument("-w, --website",
						dest='website',
						default="http://www.tagesschau.de",
						help="The website where to scrape. Currently "
							 "only tagesschau.de is supported.")
							 
	return parser.parse_args()
	

def setup():
	"""
	Style of video URLs:

	http://download.media.tagesschau.de/
		video/2013/0526/TV-20130526-2257-3401.podm.h264.mp4
	http://download.media.tagesschau.de/
		video/2013/0526/TV-20130526-2257-3401.webm.h264.mp4
	http://download.media.tagesschau.de/
		video/2013/0526/TV-20130526-2257-3401.webm.webm
	http://download.media.tagesschau.de/
		video/2013/0526/TV-20130526-2257-3401.webl.h264.mp4
	"""

	c.VIDEO_PREFIX = "TV"

	c.VIDEO_QUALITIES = {
		"mobil" : "podm.h264.mp4",
		'mittel' : "webm.h264.mp4",
		'webm' : "webm.webm",
		'hoch' : 'webl.h264.mp4'}

		
	"""
	Style of audio URLs:

	http://media.tagesschau.de/audio/2013/0526/AU-20130526-2327-3101.mp3
	http://media.tagesschau.de/audio/2013/0526/AU-20130526-2327-3101.ogg
	"""

	c.AUDIO_PREFIX = "AU"

	c.AUDIO_QUALITIES = {
		"mp3" : "mp3",
		"ogg" : "ogg"}

	c.URL_PATTERN = re.compile(r"\d*\.html")
	
	
	args = parse_args()
	
	
	c.HEADERS = {'User-Agent': args.ua}
	
	
	c.VIDEO_FILE_PATTERN = re.compile(r"http://download\.media\." + 
		"tagesschau\.de/video/\d{4}\/\d{4}/%s-\d{8}-\d{4}-\d{4}\.%s" %
		(c.VIDEO_PREFIX, c.VIDEO_QUALITIES[args.video]))
	
	c.AUDIO_FILE_PATTERN = re.compile(r"http://media\.tagesschau\.de/" + \
		"audio/\d{4}\/\d{4}/%s-\d{8}-\d{4}-\d{4}\.%s" %
		(c.AUDIO_PREFIX, c.AUDIO_QUALITIES[args.audio]))
		
		
	
	print("Video quality: ", bcolors.OKBLUE, args.video, bcolors.ENDC)
	print("Audio quality: ", bcolors.OKBLUE, args.audio, bcolors.ENDC)
	print("Downloading to:", bcolors.OKBLUE, args.dir, \
		bcolors.ENDC)
	print()
	
	return args

# Create a directory if it doesn't exist
def mkdir(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)
		


# Saves the html (as string) to a file in dir
def save_as(html, dir, name):
	f = open(dir + name, "w")
	f.write(str(html))
	f.close()
	
# Opens a url and returns it's page as a BeautifulSoup object
def cook_soup(opener, url, dir=None, name=None, data=None):
	request = urllib.request.Request(url, data, c.HEADERS)
	response = opener.open(request)

	html = response.read()
	if dir is not None and name is not None:
		save_as(html, dir, name)
		
	return BeautifulSoup(html)
	

def main(location, age, player, playlist_type, tool, website):	
	
	today = str(date.today())
	mkdir(location)
	
	playlist_file = location + today + "." + playlist_type
	playlist = open(playlist_file, "w")
	if playlist_type == 'm3u':
		playlist.write("#EXTM3U\n")
	
	# Will hold all media urls with their attributes
	medias = {}
	
	count = {}
	count[c.VIDEO_PREFIX] = 0
	count[c.AUDIO_PREFIX] = 0

	# Prepare the opener
	cj = http.cookiejar.CookieJar()
	opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
	
	soup = cook_soup(opener, website)


	# Search for news articles
	
	"""
	We want URLs with classes:
	mod modA modPremium smallImage
	mod modA modPremium smallImage
	mod modA modClassic
	mod modA modClassic
	
	We don't want URLs with classes:
	mod modD modMini
	mod modA
	"""		
		
	news = soup.find_all(attrs={"class" : 
			re.compile(r"modClassic|modPremium|modB")})

	print("Opening", len(news), "articles on", website, "|", today)
	
	# Navigate through the document and extract the urls to the 
	# articles wich will be stored in "urls"
	urls = []
	for article in news:
		teasers = article.find_all(attrs={'class' : "teaser"})
		not_lower_box = len(teasers) == 1
		for teaser in teasers:
			headlines = teaser.find_all('a')
			if not_lower_box:
				headlines = headlines[:1]
			for headline in headlines:
				if headline.has_attr("class") and \
					"icon" in headline["class"]:
					continue
				url = headline['href']
				if url.startswith("/") and not url in urls:
					urls.append(url)
					
					
	print()
	print(bcolors.BOLD_SEQ + " videos | audios | Title" + bcolors.ENDC)
	print("--------|--------|---------------")
	
	# Now look on each page if video or audio files are present
	for url in urls:
		
		name = url.split("/")[-1]
		general_topic = re.sub(c.URL_PATTERN, "", name) 
		dir = location + general_topic + "/"
		mkdir(dir)
		
		soup = cook_soup(opener, website + url, dir, name)
			
		videos = soup.find_all(attrs={'href': c.VIDEO_FILE_PATTERN})
		audios = soup.find_all(attrs={'href': c.AUDIO_FILE_PATTERN})
		
		title = soup.find("title").get_text().split(" | ")[0]
		if len(videos) + len(audios) == 0:
			print("%s   ~0~  |   ~0~  | ~%s%s" %
				  (bcolors.FAIL, title, bcolors.ENDC))
		else:
			print("   %2d   |   %2d   |  %s" % 
				(len(videos), len(audios),
				 soup.find("title").get_text().split(" | ")[0]))
		
		# Insert the found media files into their corresponding arrays
		
		media_url = videos + audios
		
		
		for m in media_url:
			m_url = m["href"]
			file = m_url.split("/")[-1]
			prefix = file[:2]
			key = general_topic + file[3:]
			if key not in medias:
				count[prefix] += 1
				time = ("%s.%s.%s %s:%s" %
					    (file[9:11], file[7:9], file[3:7], file[12:14], 
					     file[14:16]))
				medias[key] = (dir, file, m_url, 
							   "%s: %s (%s)" % (time, title, prefix))
	
	
	# We will prepare a command (that will be executed via os.system)
	# in this string
	
	# At first we are going to start vlc with a delay of 1 second, so
	# the file download can already start in the background. The output
	# vlc is sent to /dev/null so it doesn't interfere with the wget 
	# output
	fetch_command = "sleep 1 && vlc \"" + playlist_file + \
		"\" > /dev/null 2>&1 > /dev/null & "
	
	print("--------|--------|---------------")
	print("   %2d   |   %2d   | will be downloaded..." % 
		  (count[c.VIDEO_PREFIX], count[c.AUDIO_PREFIX]))
	
	# Add for all video and audio files that are not present in the 
	# filesystem an entry in the plylist and a call to wget, so it will 
	# be downloaded
	keys = sorted(medias.keys())
	for key in keys:
		e = medias[key]
		dir = e[0]
		file = e[1]
		url = e[2]
		title = e[3]
		path = dir + file
		if not os.path.exists(path):
			if playlist_type == 'm3u':
				playlist.write("#EXTINF:,,%s\n" % title)
			playlist.write(path + "\n")
			if tool == 'curl':
				fetch_command += ("cd %s && curl %s -o %s 2>&1 | grep -v "
								  "Total && " % (dir, url, file))
			elif tool == 'wget':
				fetch_command += ("cd %s && wget %s -O %s 2>&1 | grep -v "
								  "Total && " % (dir, url, file))

	playlist.close()
	
	os.system(fetch_command[:-3])
	
	return

if __name__ == '__main__':
	print(bcolors.BOLD_SEQ + "Media Scraper for tagesschau.de" +
		bcolors.ENDC)
	print(" (c) by" + bcolors.BOLD_SEQ + " Heye Voecking " +
		bcolors.ENDC + bcolors.OKBLUE + \
		"<heye.voecking+mediascraper[at]gmail[dot]com>" + bcolors.ENDC)
	print(bcolors.FAIL + \
		"This program is distributed WITHOUT ANY WARRANTY!" +
		bcolors.ENDC)
	print()
	
	args = setup()
	
	main(args.dir, args.age, args.player, args.playlist, args.tool, 
		 args.website)
