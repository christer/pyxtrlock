#!/usr/bin/env python3
# Always prefer setuptools over distutils
from setuptools import setup
# To use a consistent encoding


authors = (
    'Leon Weber <leon@leonweber.de>, '
    'Sebastian Riese <s.riese@zombofant.net>'
)

desc = (
    'The X transparent screen lock rewritten in Python, using XCB and PAM.'
)

long_desc = """
pyxtrlock -- The leightweight screen locker rewritten in Python
---------------------------------------------------------------

pyxtrlock is a very limited transparent X screen locker inspired by Ian
Jackson’s great xtrlock program. pyxtrlock uses modern libraries, most
importantly the obsolete direct passwd/shadow authentication has been replaced
by today’s PAM authentication mechanism, hence it also works on Fedora. Also,
it’s mostly written using XCB instead of Xlib.

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

setup(name='pyxtrlock',
      version='0.2',
      author=authors,
      author_email='leon@leonweber.de',
      requires=[],
      packages=['pyxtrlock'],
      license='GPLv3+',
      url='https://zombofant.net/hacking/pyxtrlock',
      description=desc,
      long_description=long_desc,
      classifiers=classifiers,
      entry_points={
          'console_scripts': [
              'pyxtrlock=pyxtrlock:main',
          ],
      },
)
