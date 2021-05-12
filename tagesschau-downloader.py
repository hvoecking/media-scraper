#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright 2013 Heye Vöcking <heye.voecking+tagesschau-downloader at gmail.com>
#
#  This program is distributed under the terms of a slightly modified version
#  of the BSD License, please see the LICENSE.md file.
#

import os
import re
import sys
import copy
import argparse
from datetime import date

import urllib.parse
import urllib.error
import urllib.request
from bs4 import BeautifulSoup

import const as c

# From http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
class bcolors:
    BOLD_SEQ = '\033[1m'
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
	NYI = "\nNOT YET IMPLEMENTED"

	parser = argparse.ArgumentParser()

	parser.add_argument("-v, --video-quality",
						choices=c.VIDEO_QUALITIES.keys(),
						default="l",
						dest='video',
					    help="There are %d different video qualities "
							 "available for download: %s" %
							 (len(c.VIDEO_QUALITIES),
							  str(c.VIDEO_QUALITIES)))

	parser.add_argument("-a, --audio-quality",
						choices=c.AUDIO_QUALITIES.keys(),
						default="mp3",
						dest='audio',
					    help="There are %d different audio qualities "
							 "available for download." %
							 len(c.AUDIO_QUALITIES))

	parser.add_argument("-d, --download-directory",
						dest='dir',
						default="~/Downloads",
						help="The directory to which the files should "
							 "be downloaded.")

	parser.add_argument("-p, --player",
						dest='player',
						default="vlc",
						help="The media player which will be called "
							 "to open the generated playlist.")

	parser.add_argument("-f, --file-age",
						dest='age',
						default=0,
						help="The maximum number of days since the "
							 "file has been published. Use 0 for "
							 "unlimited." + NYI)

	parser.add_argument("--append",
						choices=[True, False],
						dest='append',
						default=True,
						help="Whether the files downloaded in this "
						     "session should be appended to the "
						     "previous playlist." + NYI)

	parser.add_argument("--cache-age",
						dest='c_age',
						default=0,
						help="Files with an age greater than the "
							 "specified number of days will be "
							 "deleted. The default is 0, which means "
							 "no means there is no age limit." + NYI)

	parser.add_argument("--cache-size",
						dest='c_size',
						default=0,
						help="The cache size specified in megabytes. "
							 "If this size is exceeded files will be "
							 "removed in chronological order. The "
							 "default is 0, which means: thee is no "
							 "size limit." + NYI)

	parser.add_argument("--download-tool",
						choices={"curl","wget"},
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

	args = parser.parse_args()

	args.dir += "/"

	return args


def setup():

	c.TEXT_COLORS = {\
		"   " : (bcolors.ENDC, bcolors.ENDC, bcolors.ENDC), \
		"** " : (bcolors.OKBLUE, bcolors.OKBLUE, bcolors.OKBLUE), \
		"**~" : (bcolors.OKBLUE, bcolors.OKBLUE, bcolors.ENDC), \
		"  ~" : (bcolors.FAIL, bcolors.FAIL, bcolors.FAIL), \
		" * " : (bcolors.ENDC, bcolors.OKBLUE, bcolors.ENDC), \
		" *~" : (bcolors.ENDC, bcolors.OKBLUE, bcolors.OKBLUE), \
		"*  " : (bcolors.OKBLUE, bcolors.ENDC, bcolors.ENDC), \
		"* ~" : (bcolors.OKBLUE, bcolors.ENDC, bcolors.OKBLUE) \
	}

	c.PREFIX_TYPE = { " " : r"%2d", "*" : r"*%d", "-" : r"-%d" }

	"""
	Style of video URLs:
        //download.media.tagesschau.de/
                video/2018/1012/TV-20181012-2322-5601.websm.h264.mp4
        //download.media.tagesschau.de/
                video/2018/1012/TV-20181012-2322-5601.webm.h264.mp4
        //download.media.tagesschau.de/
                video/2018/1012/TV-20181012-2322-5601.webl.h264.mp4
        //download.media.tagesschau.de/
                video/2021/0127/TV-20210127-1858-5700.webxl.h264.mp4
        //download.media.tagesschau.de/
                video/2018/1012/TV-20181012-2322-5601.webxl.h264.mp4
	"""

	c.PV = 'TV'

	c.VIDEO_QUALITIES = {
		'sm' : "websm.h264.mp4",
		'm' : "webm.h264.mp4",
		'l' : "webl.h264.mp4",
		'xl' : "webxl.h264.mp4"}

	c.PLAYLIST_TYPE = "m3u"

	"""
	Style of audio URLs:

	//media.tagesschau.de/audio/2013/0526/AU-20130526-2327-3101.mp3
	//media.tagesschau.de/audio/2013/0526/AU-20130526-2327-3101.ogg
	"""

	c.PA = 'AU'

	c.AUDIO_QUALITIES = {
		'mp3' : "mp3",
		'ogg' : "ogg"}

	c.URL_PATTERN = re.compile(r"\d*\.html")


	args = parse_args()


	c.HEADERS = {'User-Agent': args.ua}


	c.VIDEO_FILE_PATTERN = re.compile(r"//download\.media\." +
		"tagesschau\.de/video/\d{4}\/\d{4}/%s-\d{8}-\d{4}-\d{4}\.%s" %
		(c.PV, c.VIDEO_QUALITIES[args.video]))

	c.AUDIO_FILE_PATTERN = re.compile(r"//media\.tagesschau\.de/"
		"audio/\d{4}\/\d{4}/%s-\d{8}-\d{4}-\d{4}\.%s" %
		(c.PA, c.AUDIO_QUALITIES[args.audio]))



	print("Video quality: ", bcolors.OKBLUE, args.video, bcolors.ENDC)
	print("Audio quality: ", bcolors.OKBLUE, args.audio, bcolors.ENDC)
	print("Downloading to:", bcolors.OKBLUE, args.dir, bcolors.ENDC)
	print()

	return args

# Create a directory if it doesn't exist
def mkdir(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)

# Saves the html (as string) to a file in dir
def save_as(html, dir, name):
	f = open(dir + name, 'w')
	f.write(str(html))
	f.close()

# Opens a url and returns it's page as a BeautifulSoup object
def cook_soup(opener, url, dir=None, name=None, data=None):
	request = urllib.request.Request(url, data, c.HEADERS)
	response = opener.open(request)

	html = response.read()
	if dir is not None and name is not None:
		save_as(html, dir, name)

	return BeautifulSoup(html, "html.parser")

def create_counter():
	counter = {}
	counter[c.PV] = 0
	counter[c.PA] = 0
	return counter

def print_table_row(videos, audios, title,
					v_prefix=" ", a_prefix=" ",
					t_prefix=" "):

	v_color, a_color, t_color = c.TEXT_COLORS[v_prefix + a_prefix + t_prefix]

	v_str = str(c.PREFIX_TYPE[v_prefix]) % videos
	a_str = str(c.PREFIX_TYPE[a_prefix]) % audios
	string = ("%s  %s  %s|%s  %s   %s|%s %s%s%s" %
			  (v_color, v_str, bcolors.ENDC,
			   a_color, a_str, bcolors.ENDC,
			   t_color, t_prefix, title, bcolors.ENDC))
	print (string)

def main(location, age, player, tool, feed):
	today = str(date.today())
	mkdir(location)

	playlist_file = location + today + "." + c.PLAYLIST_TYPE
	playlist = open(playlist_file, 'w')
	playlist.write("#EXTM3U\n")

	# Will hold all media urls with their attributes
	medias = {}

	count = create_counter()
	duplicates = 0

	# Prepare the opener
	opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(None))

	soup = cook_soup(opener, feed)

	urls = []
	for entry in soup.find_all('entry'):
		urls.append(entry.link['href'])

	print("Opening", len(urls), "articles on", feed, "|", today)
	print()
	print("%svideo %s| %saudio %s|%s Title%s" %
		  (bcolors.BOLD_SEQ, bcolors.ENDC,
		   bcolors.BOLD_SEQ, bcolors.ENDC,
		   bcolors.BOLD_SEQ, bcolors.ENDC))
	print("------|-------|---------------")

	# Now look on each page if video or audio files are present
	for url in urls:

		if not url.endswith(".html"):
			print ("Skipping non-html document, with url", url)
			continue
		if not url.startswith("https://www.tagesschau.de"):
			print ("Skipping non-tagesschau url", url)
			continue

		name = url.split("/")[-1]
		general_topic = re.sub(c.URL_PATTERN, "", name)
		dir = location + general_topic + "/"
		mkdir(dir)

		soup = cook_soup(opener, url, dir, name)

		videos = soup.find_all(attrs={'href': c.VIDEO_FILE_PATTERN})
		audios = soup.find_all(attrs={'href': c.AUDIO_FILE_PATTERN})

		title = soup.find('title').get_text().split(" | ")[0]

		# Insert the found media files into their corresponding arrays

		media_url = videos + audios

		before = copy.copy(count)

		for m in media_url:
			m_url = m['href']
			if not m_url.startswith("http"):
				m_url = "https:" + m_url
			file = m_url.split("/")[-1]
			prefix = file[:2]
			key = file[3:]
			if not (key in medias or (os.path.exists(dir + file) and os.path.getsize(dir + file) > 0)):
				count[prefix] += 1
				time = ("%s.%s.%s %s:%s" %
					    (file[9:11], file[7:9], file[3:7], file[12:14],
					     file[14:16]))
				medias[key] = (dir, file, m_url,
							   "(%s) %s: %s" %
							   (prefix, time, title),
							   general_topic)
			else:
				duplicates += 1

		len_v = len(videos)
		count_v = count[c.PV] - before[c.PV]
		len_a = len(audios)
		count_a = count[c.PA] - before[c.PA]

		if len_v + len_a == 0:
			print_table_row(len_v, len_a, title, " ", " ", "~")
		else:
			pv = "*" if len_v != count_v else " "
			pa = "*" if len_a != count_a else " "
			pt = "~" if len_a * len_v != 0 and before == count else " "
			print_table_row(count_v, count_a, title, pv, pa, pt)

	# We will prepare a command (that will be executed via os.system)
	# in this string

	# At first we are going to start vlc with a delay of 1 second, so
	# the file download can already start in the background. The output
	# vlc is sent to /dev/null so it doesn't interfere with the wget
	# output
	cmd = ["sleep 1 && vlc \"%s\" > /dev/null 2>&1 > /dev/null & " %
		  playlist_file]

	print("------|-------|---------------")
	print_table_row(count[c.PV], count[c.PA], "will be downloaded...");
	if duplicates != 0:
		print("%s* %d files have been skipped because they were "
			  "duplicates...%s" %
			  (bcolors.OKBLUE, duplicates, bcolors.ENDC))


	# Sort the media keys to be grouped by topic
	sorted_medias = {}
	for key in medias.keys():
		general_topic = medias[key][4]
		sorted_medias[general_topic + key] = medias[key]

	keys = sorted(sorted_medias.keys())
	medias = sorted_medias

	# Add for all video and audio files that are not present in the
	# filesystem an entry in the plylist and a call to wget, so it will
	# be downloaded
	for key in keys:
		e = medias[key]
		dir = e[0]
		file = e[1]
		url = e[2]
		title = e[3]
		path = dir + file
		escaped_title = title.replace("-", "‑")
		playlist.write("#EXTINF:,,%s\n" % escaped_title)
		playlist.write(path + "\n")
		option = ""
		grep = ""
		if tool == 'curl':
			option = "-o"
			grep = "-v Total"
		elif tool == 'wget':
			option = "-O"
			grep =  "saved"
		cmd.append("cd %s && %s %s %s %s 2>&1 | grep %s && " %
				   (dir, tool, url, option, file, grep))

	playlist.close()


	command = ''.join(cmd) + "echo done"

	os.system(command)

	return

if __name__ == '__main__':
	print(bcolors.BOLD_SEQ + "Media Scraper for tagesschau.de" +
		bcolors.ENDC)
	print(" (c) by" + bcolors.BOLD_SEQ + " Heye Voecking " +
		bcolors.ENDC + bcolors.OKBLUE + \
		"<heye.voecking+tagesschau-downloader[at]gmail[dot]com>" + bcolors.ENDC)
	print()
	print(bcolors.FAIL + \
		"This program is distributed WITHOUT ANY WARRANTY!" +
		bcolors.ENDC)
	print()

	args = setup()

	main(args.dir, args.age, args.player, args.tool,
		 "http://www.tagesschau.de/xml/atom/")
