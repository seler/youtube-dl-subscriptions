#!/usr/bin/env python3

# https://www.python.org/dev/peps/pep-0008/#version-bookkeeping
# https://www.python.org/dev/peps/pep-0440/
__version_info__ = (0, 3)
__version__ = '.'.join(map(str, __version_info__))

import argparse

import feedparser
import opml
import youtube_dl

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

Base = declarative_base()


class Video(Base):
    __tablename__ = 'video'
    id = Column(Integer, primary_key=True)
    url = Column(String(250), nullable=False, unique=True)


def main():
    parser = argparse.ArgumentParser()
    # standard options
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true")
    group.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument('--version', action='version',
                        version='%(prog)s {}'.format(__version__))

    parser.add_argument('--opml-file', default='subs.xml')
    parser.add_argument('--database', default='sqlite:///ytdls.db')
    parser.add_argument('-o', '--output', metavar='TEMPLATE', dest='outtmpl',
                        help='YoutubeDL output filename template, see the '
                             'YoutubeDL "OUTPUT TEMPLATE" for all the info')

    args = parser.parse_args()
    dl(args.opml_file, args.database, args.outtmpl)


def dl(opml_filename, database, outtmpl):
    engine = create_engine(database)
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine
    session = sessionmaker(bind=engine)()

    channels = opml.parse(opml_filename)[0]

    videos = []

    for i, channel in enumerate(channels):
        feed = feedparser.parse(channel.xmlUrl)
        for item in feed['items']:
            url = item['link']
            session.add(Video(url=url))
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
            else:
                videos.append(url)

    ydl_opts = {}
    if outtmpl:
        ydl_opts['outtmpl'] = outtmpl

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(videos)


if __name__ == '__main__':
    main()
