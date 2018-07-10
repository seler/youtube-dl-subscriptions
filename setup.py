#!/usr/bin/env python3

from setuptools import setup

setup(
    name='youtube-dl-subscriptions',
    version='0.4',
    description='Downloads all new videos from your YouTube subscription feeds.',
    url='https://github.com/mewfree/youtube-dl-subscriptions',
    py_modules=['youtube_dl_subscriptions'],
    entry_points={'console_scripts': [
        'youtube-dl-subscriptions = youtube_dl_subscriptions:main',
    ]},
    install_requires=[
        'opml',
        'feedparser',
        'youtube-dl',
        'sqlalchemy',
    ],
)
