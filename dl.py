#!/usr/bin/env python3

# https://www.python.org/dev/peps/pep-0008/#version-bookkeeping
# https://www.python.org/dev/peps/pep-0440/
__version_info__ = (0, 3)
__version__ = '.'.join(map(str, __version_info__))

import argparse
import sys
from datetime import datetime
from glob import glob
from time import mktime, time

import feedparser
import opml
import youtube_dl


def main():
    parser = argparse.ArgumentParser()
    # standard options
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true")
    group.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument('--version', action='version',
                        version='%(prog)s {}'.format(__version__))

    parser.add_argument('--opml-file', default='subs.xml')
    parser.add_argument('--last-file', default='last.txt')
    parser.add_argument('-o', '--output', metavar='TEMPLATE', dest='outtmpl',
                        help='YoutubeDL output filename template, see the '
                             'YoutubeDL "OUTPUT TEMPLATE" for all the info')

    args = parser.parse_args()
    dl(args.opml_file, args.last_file, args.outtmpl)


def dl(opml_filename, last_filename, outtmpl):
    try:
        f = open(last_filename)
    except FileNotFoundError:
        with open(last_filename, 'w') as f:
            f.write(str(time()))
            print('Initialized a {} file with current timestamp.'.format(last_filename))
    else:
        content = f.read()
        f.close()

        channels = opml.parse(opml_filename)[0]

        ptime = datetime.utcfromtimestamp(float(content))
        ftime = time()

        urls = []
        videos = []

        for i, channel in enumerate(channels):
            print('Parsing through channel {} out of {}'.format(i + 1, len(channels)), end='\r')
            feed = feedparser.parse(channel.xmlUrl)
            for item in feed['items']:
                timef = item['published_parsed']
                dt = datetime.fromtimestamp(mktime(timef))
                if dt > ptime:
                    videos.append(item['link'])

        print('')  # print newline

        if videos:
            print('{} new videos found'.format(len(videos)))
        else:
            print('Sorry, no new video found')

        ydl_opts = {}
        if outtmpl:
            ydl_opts['outtmpl'] = outtmpl

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(videos)

        with open(last_filename, 'w') as f:
            f.write(str(ftime))


if __name__ == '__main__':
    main()
