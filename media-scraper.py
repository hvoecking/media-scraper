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


import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, re, os, sys, time, http.cookiejar
import argparse
from datetime import date
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

# Constants
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; ru; rv:1.9.2.3) \
Gecko/20100401 Firefox/4.0 (.NET CLR 3.5.30729)'
headers = {'User-Agent': user_agent}
host = 'http://www.tagesschau.de'

"""
Style of video links:

http://download.media.tagesschau.de/
	video/2013/0526/TV-20130526-2257-3401.podm.h264.mp4
http://download.media.tagesschau.de/
	video/2013/0526/TV-20130526-2257-3401.webm.h264.mp4
http://download.media.tagesschau.de/
	video/2013/0526/TV-20130526-2257-3401.webm.webm
http://download.media.tagesschau.de/
	video/2013/0526/TV-20130526-2257-3401.webl.h264.mp4
"""

video_prefix = "TV"

video_qualities = {
	"mobil" : "podm.h264.mp4",
	'mittel' : "webm.h264.mp4",
	'webm' : "webm.webm",
	'hoch' : 'webl.h264.mp4'}

	
"""
Style of audio links:

http://media.tagesschau.de/audio/2013/0526/AU-20130526-2327-3101.mp3
http://media.tagesschau.de/audio/2013/0526/AU-20130526-2327-3101.ogg
"""

audio_prefix = "AU"

audio_qualities = {
	"mp3" : "mp3",
	"ogg" : "ogg"}

url_pattern = re.compile(r"\d*\.html")


# Create a directory if it doesn't exist
def mkdir(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)
		


# Saves the html (as string) to a file in dir
def save_as(html, dir, name):
	f = open(dir + name, "w")
	f.write(str(html))
	f.close()
	
# Opens a link and returns it's page as a BeautifulSoup object
def cook_soup(opener, link, dir=None, name=None, data=None):
	request = urllib.request.Request(link, data, headers)
	response = opener.open(request)

	html = response.read()
	if dir is not None and name is not None:
		save_as(html, dir, name)
		
	return BeautifulSoup(html)
	

def main(audio_quality, video_quality, location, age, player,
		 playlist, tool):	
	
	
	video_file_pattern = re.compile(r"http://download\.media\." + 
		"tagesschau\.de/video/\d{4}\/\d{4}/%s-\d{8}-\d{4}-\d{4}\.%s" %
		(video_prefix, video_qualities[video_quality]))
	
	audio_file_pattern = re.compile(r"http://media\.tagesschau\.de/" + \
		"audio/\d{4}\/\d{4}/%s-\d{8}-\d{4}-\d{4}\.%s" %
		(audio_prefix, audio_qualities[audio_quality]))
	
	print("Audio quality: ", bcolors.OKBLUE, audio_quality, bcolors.ENDC)
	print("Video quality: ", bcolors.OKBLUE, video_quality, bcolors.ENDC)
	print("Downloading to:", bcolors.OKBLUE, location, \
		bcolors.ENDC)
	print()
	
	today = str(date.today())
	# Setup directory and playlist
	mkdir(location)
	playlist_file = location + today + ".m3u"
	playlist = open(playlist_file, "w")
	playlist.write("#EXTM3U\n")
	
	# Will hold all media urls with their attributes
	medias = {}
	
	count = {}
	count[video_prefix] = 0
	count[audio_prefix] = 0

	# Prepare the opener
	cj = http.cookiejar.CookieJar()
	opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
	
	soup = cook_soup(opener, host)


	# Search for news articles
	
	"""
	We want links with classes:
	mod modA modPremium smallImage
	mod modA modPremium smallImage
	mod modA modClassic
	mod modA modClassic
	
	We don't want links with classes:
	mod modD modMini
	mod modA
	"""		
		
	news = soup.find_all(attrs={"class" : 
			re.compile(r"modClassic|modPremium|modB")})

	print("Opening", len(news), "articles on", host, "|", today)
	
	# Navigate through the document and extract the urls to the 
	# articles wich will be stored in "links"
	links = []
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
				link = headline['href']
				if link.startswith("/") and not link in links:
					links.append(link)
					
					
	print()
	print(bcolors.BOLD_SEQ + " audios | videos | Title" + bcolors.ENDC)
	print("--------|--------|---------------")
	
	# Now look on each page if video or audio files are present
	for link in links:
		
		name = link.split("/")[-1]
		general_topic = re.sub(url_pattern, "", name) 
		dir = location + general_topic + "/"
		mkdir(dir)
		
		soup = cook_soup(opener, host + link, dir, name)
			
		videos = soup.find_all(attrs={'href': video_file_pattern})
		audios = soup.find_all(attrs={'href': audio_file_pattern})
		
		title = soup.find("title").get_text().split(" | ")[0]
		if len(audios) + len(videos) == 0:
			print("%s   ~0~  |   ~0~  | ~%s%s" %
				  (bcolors.FAIL, title, bcolors.ENDC))
		else:
			print("   %2d   |   %2d   |  %s" % 
				(len(audios), len(videos), 
				 soup.find("title").get_text().split(" | ")[0]))
		
		# Insert the found media files into their corresponding arrays
		
		media_url = audios + videos
		
		
		for m in media_url:
			url = m["href"]
			file = url.split("/")[-1]
			prefix = file[:2]
			key = general_topic + file[3:]
			if key not in medias:
				count[prefix] += 1
				time = ("%s.%s.%s %s:%s" %
					    (file[9:11], file[7:9], file[3:7], file[12:14], 
					     file[14:16]))
				medias[key] = (dir, file, url, 
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
		  (count[audio_prefix], count[video_prefix]))
	
	# Add for all audio and video files that are not present in the 
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
			playlist.write("#EXTINF:,,%s\n" % title)
			playlist.write(path + "\n")
			fetch_command += ("cd %s && curl %s -o %s 2>&1 | grep -v "
							  "Total && " % (dir, url, file))

	playlist.close()
	
	#os.system(fetch_command[:-3])
	
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
	
	
	# Arguments
	parser = argparse.ArgumentParser(description="Optional arguments")

	parser.add_argument("-a, --audio-quality",
						choices=audio_qualities.keys(),
						default='mp3',
						dest='audio',
					    help="There are %d different audio qualities "
							 "available for download." % 
							 len(audio_qualities))
							 
	parser.add_argument("-v, --video-quality",
						choices=video_qualities.keys(),
						default='webm',
						dest='video',
					    help="There are %d different video qualities "
							 "available for download: %s" % 
							 (len(video_qualities), 
							  str(video_qualities)))
	location = "/tmp/tagesschau"
	parser.add_argument("-d, --download-directory",
						dest='dir',
						default=location,
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
						dest='tool',
						default="curl",
						help="The command line tool used to download "
							 "the media files. Only tested with curl "
							 "and wget so far.")
							 
	args = parser.parse_args()
	
	main(args.audio, args.video, args.dir, args.age, args.player, 
		 args.playlist, args.tool)
