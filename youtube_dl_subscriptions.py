#!/usr/bin/env python3

# https://www.python.org/dev/peps/pep-0008/#version-bookkeeping
# https://www.python.org/dev/peps/pep-0440/
__version_info__ = (0, 3)
__version__ = '.'.join(map(str, __version_info__))

import argparse

import feedparser
import opml
import youtube_dl
from sqlalchemy.exc import IntegrityError
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(message)s')

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
    parser.add_argument('--fake', action="store_true")
    parser.add_argument('-o', '--output', metavar='TEMPLATE', dest='outtmpl',
                        help='YoutubeDL output filename template, see the '
                             'YoutubeDL "OUTPUT TEMPLATE" for all the info')

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
    if args.quiet:
        logger.setLevel(logging.ERROR)

    dl(args.opml_file, args.database, args.outtmpl,
       args.fake, args.quiet, args.verbose)


def dl(opml_filename, database, outtmpl,
       fake=False, quiet=False, verbose=False):
    engine = create_engine(database)
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine
    session = sessionmaker(bind=engine)()

    opts = {}
    if outtmpl:
        opts['outtmpl'] = outtmpl
    if quiet:
        opts['quiet'] = quiet
    if verbose:
        opts['verbose'] = verbose

    for channel in opml.parse(opml_filename)[0]:
        logger.debug('Parsing channel "{}".'.format(channel.title))
        for item in feedparser.parse(channel.xmlUrl)['items']:
            session.add(Video(url=item['link']))
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
            else:
                msg = 'Downloading "{}" from "{}".'
                logger.info(msg.format(item['title'], channel.title))
                if not fake:
                    try:
                        download(item['link'], opts)
                    except Exception:
                        session.rollback()


def download(url, opts):
    with youtube_dl.YoutubeDL(opts) as ydl:
        ydl.download([url])


if __name__ == '__main__':
    main()
