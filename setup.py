#! /usr/bin/env python3

from distutils.core import setup

setup(name='iheart-mplayer',
      url='https://github.com/oldlaptop/iheart-mplayer',
      py_modules=['parse_iheart_json'],
      scripts=['./iheart-url', './iheart-mplayer', './iheart-mpv', './iheart-vlc'],
      )
