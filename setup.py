#!/usr/bin/env python3

from setuptools import setup

setup(
    name='youtube-dl-subscriptions',
    version='0.3',
    description='Downloads all new videos from your YouTube subscription feeds.',
    url='https://github.com/mewfree/youtube-dl-subscriptions',
    py_modules=['dl'],
    entry_points={'console_scripts': [
        'youtube-dl-subscriptions = dl:main',
    ]},
    install_requires=[
        'opml',
        'feedparser',
        'youtube-dl',
        'sqlalchemy',
    ],
)
