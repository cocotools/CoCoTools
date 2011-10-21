#!/usr/bin/env python
"""Tools for analyzing data from the CoCoMac macaque connectivity database.
"""
from distutils.core import setup

setup(name='CoCoTools',
      version='-1',
      description='CoCoMac Access and Analysis Tools',
      author='Daniel Bliss and Fernando Perez',
      author_email='dbliss@berkeley.edu',
      maintainer='Daniel Bliss and Fernando Perez',
      maintainer_email='dbliss@berkeley.edu',
      url='',
      packages=['cocotools'],
      requires=['brainx', 'networkx'],
      provides=['cocotools'],
      package_data={'cocotools': ['tests/doc.txt']}
      )
