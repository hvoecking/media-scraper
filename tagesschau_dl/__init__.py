#!/usr/bin/env python
# coding: utf-8

import argparse
import copy
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from html import unescape

from bs4 import BeautifulSoup

BOLD = "\033[1m"
HEADER = "\033[95m"
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
END = "\033[0m"

TEXT_COLORS = {
    "   ": (END, END, END),
    "** ": (BLUE, BLUE, BLUE),
    "**~": (BLUE, BLUE, END),
    "  ~": (RED, RED, RED),
    " * ": (END, BLUE, END),
    " *~": (END, BLUE, BLUE),
    "*  ": (BLUE, END, END),
    "* ~": (BLUE, END, BLUE),
}

PREFIX_TYPE = {" ": r"%2d", "*": r"*%d", "-": r"-%d"}

PV = "TV"
PA = "AU"

URL_PATTERN = re.compile(r"\d*\.html")
AUDIO_QUALITIES = {"mp3": "mp3", "ogg": "ogg"}
VIDEO_QUALITIES = {
    "sm": "websm.h264.mp4",
    "m": "webm.h264.mp4",
    "l": "webl.h264.mp4",
    "xl": "webxl.h264.mp4",
}

PLAYLIST_TYPE = "m3u"
TAGESSCHAU_BASE = "https://www.tagesschau.de"
FEED = f"{TAGESSCHAU_BASE}/xml/atom/"


def compile_pattern(type, prefix, quality):
    return re.compile(
        r"//download\.media\.tagesschau\.de/%s/\d{4}\/\d{4}/%s-\d{8}-\d{4}-\d{4}\.%s"
        % (type, prefix, quality)
    )


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-v, --video-quality",
        choices=VIDEO_QUALITIES.keys(),
        default="xl",
        dest="video",
        help=" ".join(
            [
                f"There are {len(VIDEO_QUALITIES)} different video qualities available",
                f"for download: {str(VIDEO_QUALITIES)}",
            ]
        ),
    )

    parser.add_argument(
        "-a, --audio-quality",
        choices=AUDIO_QUALITIES.keys(),
        default="mp3",
        dest="audio",
        help=" ".join(
            [
                f"There are {len(AUDIO_QUALITIES)} different audio qualities available",
                "for download.",
            ]
        ),
    )

    parser.add_argument(
        "-d, --download-directory",
        dest="dir",
        default=os.path.join(os.path.expanduser("~"), "Downloads"),
        help="The directory to which the files should be downloaded.",
    )

    parser.add_argument(
        "-p, --player",
        dest="player",
        default="vlc",
        help="The media player which will be called to open the generated playlist.",
    )

    parser.add_argument(
        "--download-tool",
        choices={"curl", "wget"},
        dest="tool",
        default="curl",
        help=" ".join(
            [
                "The command line tool used to download the media files. Command line",
                "output is optimized for curl.",
            ]
        ),
    )

    default_ua = " ".join(
        [
            "Mozilla/5.0 (Windows; U; Windows NT 6.1; ru; rv:1.9.2.3)",
            "Gecko/20100401",
            "Firefox/4.0 (.NET CLR 3.5.30729)",
        ]
    )
    parser.add_argument(
        "-u, --user-agent",
        dest="ua",
        default=default_ua,
        help="The user agent to be used.",
    )

    return parser.parse_args()


# Create a directory if it doesn't exist
def mkdir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


# Opens a url and returns it's page as a BeautifulSoup object
def cook_soup(opener, url, headers, dir=None, name=None, data=None):
    request = urllib.request.Request(url, data, headers)
    response = opener.open(request)

    resp = response.read().decode("utf-8")
    html = unescape(resp)
    if dir is not None and name is not None:
        with open(dir + name, "w") as f:
            f.write(str(html))

    return BeautifulSoup(html, "html.parser")


def print_table_row(videos, audios, title, v_prefix=" ", a_prefix=" ", t_prefix=" "):
    v_color, a_color, t_color = TEXT_COLORS[v_prefix + a_prefix + t_prefix]

    v_str = str(PREFIX_TYPE[v_prefix]) % videos
    a_str = str(PREFIX_TYPE[a_prefix]) % audios
    print(
        "|".join(
            [
                f"{v_color}  {v_str}  {END}",
                f"{a_color}  {a_str}   {END}",
                f"{t_color} {t_prefix}{title}{END}",
            ]
        )
    )


def main():
    args = parse_args()

    print(f"{BOLD}Downloader for tagesschau.de{END}")
    print(
        f" (c) by{BOLD} Heye Voecking {END}{BLUE}<heye.voecking[at]gmail[dot]com>{END}"
    )
    print()
    print(f"{RED}This program is distributed WITHOUT ANY WARRANTY!{END}")
    print()
    print(f"Video quality:  {BLUE}{args.video}{END}")
    print(f"Audio quality:  {BLUE}{args.audio}{END}")
    print(f"Downloading to: {BLUE}{args.dir}{END}")
    print()

    args.dir += "/"
    headers = {"User-Agent": args.ua}
    video_pattern = compile_pattern("video", PV, VIDEO_QUALITIES[args.video])
    audio_pattern = compile_pattern("audio", PA, AUDIO_QUALITIES[args.audio])

    today = str(date.today())
    mkdir(args.dir)

    playlist_file = args.dir + today + "." + PLAYLIST_TYPE
    playlist = open(playlist_file, "w")
    playlist.write("#EXTM3U\n")

    # Will hold all media urls with their attributes
    medias = {}

    count = {
        PV: 0,
        PA: 0,
    }
    duplicates = 0

    # Prepare the opener
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(None))

    soup = cook_soup(opener, FEED, headers)

    urls = []
    for entry in soup.find_all("entry"):
        urls.append(entry.link["href"])

    print(f"Opening {len(urls)} articles on {FEED} | {today}")
    print()
    print(f"{BOLD}video {END}| {BOLD}audio {END}|{BOLD} Title{END}")
    print("------|-------|---------------")

    # Now look on each page if video or audio files are present
    for url in urls:

        if not url.endswith(".html"):
            print(f"Skipping non-html document, with url {url}")
            continue
        if not url.startswith(TAGESSCHAU_BASE):
            print(f"Skipping non-tagesschau url {url}")
            continue

        name = url.split("/")[-1]
        general_topic = re.sub(URL_PATTERN, "", name)
        dir = f"{args.dir}{general_topic}/"
        mkdir(dir)
        try:
            soup = cook_soup(opener, url, headers, dir, name)
        except urllib.error.URLError as err:
            print(f"Failed to open '{url}':{err}")
            continue

        videos = soup.find_all(attrs={"data-config": video_pattern})
        audios = soup.find_all(attrs={"data-config": audio_pattern})

        title = soup.find("title").get_text().split(" | ")[0]

        # Insert the found media files into their corresponding arrays
        media_url = videos + audios

        before = copy.copy(count)
        for m in media_url:
            m_url = json.loads(m["data-config"])["mc"]["_mediaArray"][0][
                "_mediaStreamArray"
            ][-1]["_stream"]
            if not m_url.startswith("http"):
                m_url = "https:" + m_url
            file = m_url.split("/")[-1]
            prefix = file[:2]
            key = file[3:]
            path = dir + file
            if key in medias or (os.path.exists(path) and os.path.getsize(path) > 0):
                duplicates += 1
                continue

            count[prefix] += 1
            time = f"{file[9:11]}.{file[7:9]}.{file[3:7]} {file[12:14]}:{file[14:16]}"
            medias[key] = (
                dir,
                file,
                m_url,
                f"({prefix}) {time}: {title}",
                general_topic,
            )

        len_v = len(videos)
        count_v = count[PV] - before[PV]
        len_a = len(audios)
        count_a = count[PA] - before[PA]

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
    cmd = [f'sleep 1 && vlc "{playlist_file}" > /dev/null 2>&1 > /dev/null & ']

    print("------|-------|---------------")
    print_table_row(count[PV], count[PA], "will be downloaded...")
    if duplicates != 0:
        print(f"{BLUE}* {duplicates} duplicates skipped...{END}")

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
        playlist.write(f"#EXTINF:,,{escaped_title}\n")
        playlist.write(path + "\n")
        option = ""
        grep = ""
        if args.tool == "curl":
            option = "-o"
            grep = "-v Total"
        elif args.tool == "wget":
            option = "-O"
            grep = "saved"
        cmd.append(
            f"cd {dir} && {args.tool} {url} {option} {file} 2>&1 | grep {grep} && "
        )

    playlist.close()
    os.system("".join(cmd) + "echo done")


if __name__ == "__main__":
    main()
