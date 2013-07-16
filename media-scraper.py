#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  wg-searcher.py
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
from datetime import date
from bs4 import BeautifulSoup

# From http://stackoverflow.com/questions/287871/print-in-terminal-
# 												with-colors-using-python
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

video_qualities = {
	"MOBIL" : "podm.h264.mp4",
	'MITTEL4' : "webm.h264.mp4",
	'MITTEL' : "webm.webm",
	'HOCH' : 'webl.h264.mp4'}

video_quality = "MITTEL"	

video_file_pattern = re.compile(r"http://download\.media\." + \
	"tagesschau\.de/video/\d{4}\/\d{4}/TV-\d{8}-\d{4}-\d{4}\." + \
	video_qualities[video_quality])
		
	
"""
Style of audio links:

http://media.tagesschau.de/audio/2013/0526/AU-20130526-2327-3101.mp3
http://media.tagesschau.de/audio/2013/0526/AU-20130526-2327-3101.ogg
"""

audio_qualities = {
	"MP3" : "mp3",
	"OGG" : "ogg"}

audio_quality = "MP3"

audio_file_pattern = re.compile(r"http://media\.tagesschau\.de/" + \
	"audio/\d{4}\/\d{4}/AU-\d{8}-\d{4}-\d{4}\." + \
	audio_qualities[audio_quality])

	
today = str(date.today())

# Create a directory if it doesn't exist
def mkdir(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)
		

# Setup directory and playlist
location = "/tmp/tagesschau/"
mkdir(location)
playlist_file = location + today + ".m3u"
playlist = open(playlist_file, "w")
playlist.write("#EXTM3U\n")

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
	

def main():	
	# Will hold all media urls with their attributes
	medias = {}

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
		dir = location + name.replace(".html", "") + "/"
		mkdir(dir)
		
		soup = cook_soup(opener, host + link, dir, name)
			
		videos = soup.find_all(attrs={'href': video_file_pattern})
		audios = soup.find_all(attrs={'href': audio_file_pattern})
		
		title = soup.find("title").get_text().split(" | ")[0]
		if len(audios) + len(videos) == 0:
			print(bcolors.FAIL + "   ~0~  |   ~0~  | ~" + title + \
				bcolors.ENDC)
		else:
			print("    " + str(len(audios)) + "   |    " + \
				str(len(videos)) + "   | ", \
				soup.find("title").get_text().split(" | ")[0])
		
		# Insert the found media files into their corresponding arrays
		
		media_url = audios + videos
		
		
		for m in media_url:
			url = m["href"]
			file = url.split("/")[-1]
			key = file[3:]
			if key not in medias:
				date = file[9:11] + "." + file[7:9] + "." + file[3:7] + \
					   " " + file[12:14] + ":" + file[14:16]
				medias[key] = (dir, file, url, date + ": " + title)
	
	
	# We will prepare a command (that will be executed via os.system)
	# in this string
	
	# At first we are going to start vlc with a delay of 1 second, so
	# the file download can already start in the background. The output
	# vlc is sent to /dev/null so it doesn't interfere with the wget 
	# output
	fetch_command = "sleep 1 && vlc \"" + playlist_file + \
		"\" > /dev/null 2>&1 > /dev/null & "
	
	print("--------|--------|---------------")
	#print("    " + str(len(audio_files)) + "   |   " + 
	#	str(len(video_files)) + "   | will be downloaded...")
	
	# Add for all audio and video files that are not present in the 
	# filesystem an entry in the plylist and a call to wget, so it will 
	# be downloaded
	keys = sorted(medias.keys())
	for key in keys:
		e = medias[key]
		dir = e[0]
		file = e[1].split("/")[-1]
		url = e[2]
		title = e[3]
		path = dir + file
		if not os.path.exists(path):
			playlist.write("#EXTINF:,,%s\n" % title)
			playlist.write(path + "\n")
			fetch_command += ("cd %s && curl %s -o %s 2>&1 | grep -v "
							  "Total && " % (dir, url, file))

	playlist.close()
	
	os.system(fetch_command[:-3])
	
	return


if __name__ == '__main__':
	print(bcolors.BOLD_SEQ + "Media Scraper for tagesschau.de" + \
		bcolors.ENDC)
	print(" (c) by" + bcolors.BOLD_SEQ + " Heye Voecking " + \
		bcolors.ENDC + bcolors.OKBLUE + \
		"<heye.voecking+mediascraper[at]gmail[dot]com>" + bcolors.ENDC)
	print(bcolors.FAIL + \
		"This program is distributed WITHOUT ANY WARRANTY!" + \
		bcolors.ENDC)
	print()
	
	print("Audio quality: ", bcolors.OKBLUE, audio_quality, bcolors.ENDC)
	print("Video quality: ", bcolors.OKBLUE, video_quality, bcolors.ENDC)
	print("Downloading to:", bcolors.OKBLUE, location, \
		bcolors.ENDC)
	print()
	main()
