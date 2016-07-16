#!/usr/bin/env python3
# Always prefer setuptools over distutils
from setuptools import setup
# To use a consistent encoding


authors = (
    'Leon Weber <leon@leonweber.de>, '
    'Sebastian Riese <s.riese@zombofant.net>'
)

desc = (
    'Extremely lightweigt xorg locker.'
)

long_desc = """
simplelock -- The extremely lightweight xorg locker written in Python
----------------------------------------------------------------------

simplelock is a very limited transparent xorg keyboard/mouse locker based on pyxtrlock.

"""


classifiers = [
    'Development Status :: 3',
    'Environment :: X11 Applications',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 3',
    'Topic :: Desktop Environment :: Screen Savers'
]

setup(name='simplelock',
      version='1.0',
      author=authors,
      author_email='hcs@furuvik.net',
      requires=[
        'passlib',
      ],
      packages=['simplelock'],
      license='GPLv3+',
      url='https://github.com/christer/simplelock',
      description=desc,
      long_description=long_desc,
      classifiers=classifiers,
      entry_points={
          'console_scripts': [
              'simplelock=simplelock:main',
          ],
      },
)
