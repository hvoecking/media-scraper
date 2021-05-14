# Tagesschau Downloader

Python script for playing and downloading all media on tagesschau.de with a single click.


I always imagined how nice it would be, if I got up and only needed a single click to enjoy my news during breakfast. And finally I came around to do it.

## Installation

Example for Ubuntu:
```bash
git clone https://github.com/hvoecking/tagesschau-downloader.git
cd tagesschau-downloader
# install pip3 if not already present, eg. sudo apt-get install python3-pip
sudo pip3 install virtualenv
virtualenv venv
source venv/bin/activate
python3 tagesschau-downloader.py [--help]
```

## Download

Using the standard options the ammount downloaded per day will average at about 80MB to 90MB.
Ranging from 20MB up to 150MB or more.

## License

MIT

## TODO

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
- [x] Format code
- [x] Consistently sort video stuff before audio stuff
