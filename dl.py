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
    if len(glob(last_filename)) == 0:
        f = open(last_filename, 'w')
        f.write(str(time()))
        print('Initialized a {} file with current timestamp.'.format(last_filename))
        f.close()

    else:
        f = open(last_filename)
        content = f.read()
        f.close()

        outline = opml.parse(opml_filename)

        ptime = datetime.utcfromtimestamp(float(content))
        ftime = time()

        urls = []

        for i in range(0, len(outline[0])):
            urls.append(outline[0][i].xmlUrl)

        videos = []
        for i in range(0, len(urls)):
            print('Parsing through channel '+str(i+1)+' out of '+str(len(urls)), end='\r')
            feed = feedparser.parse(urls[i])
            for j in range(0, len(feed['items'])):
                timef = feed['items'][j]['published_parsed']
                dt = datetime.fromtimestamp(mktime(timef))
                if dt > ptime:
                    videos.append(feed['items'][j]['link'])

        if len(videos) == 0:
            print('Sorry, no new video found')
        else:
            print(str(len(videos))+' new videos found')

        ydl_opts = {}
        if outtmpl:
            ydl_opts['outtmpl'] = outtmpl

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(videos)

        f = open('last.txt', 'w')
        f.write(str(ftime))
        f.close()


if __name__ == '__main__':
    main()
