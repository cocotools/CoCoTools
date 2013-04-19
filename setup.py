#!/usr/bin/env python
"""Tools for analyzing data from the CoCoMac macaque connectivity database.
"""
from distutils.core import setup

setup(name='CoCoTools',
      version='-1',
      description='CoCoMac Access and Analysis Tools',
      author='Daniel Bliss, Robert Blumenfeld and Fernando Perez',
      author_email='dbliss@berkeley.edu, rsblume@berkeley.edu',
      maintainer='Robert Blumenfeld, Daniel Bliss, and Fernando Perez',
      maintainer_email='rsblume@berkeley.edu, dbliss@berkeley.edu, ',
      url='http://cocotools.github.io/',
      packages=['cocotools'],
      requires=['networkx'],
      provides=['cocotools'],
      package_data={'cocotools': ['tests/doc.txt']}
      )
