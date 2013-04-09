#!/usr/bin/env python
"""Script to make the docs on systems lacking the Make utility.
"""
#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import os
import shutil
import sys
from subprocess import check_call

#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------
def sh(cmd):
    """Execute command in a subshell, return status code."""
    print 'CMD:', cmd
    return check_call(cmd, shell=True)


def html():
    sh('sphinx-build -b html -d build/doctrees source build/html')


def clean():
    if os.path.isdir('build'):
        shutil.rmtree('build')


def website():
    clean()
    html()
    sh('python website.py')

#-----------------------------------------------------------------------------
# Script starts
#-----------------------------------------------------------------------------

if __name__ == '__main__':
    try:
        tname = sys.argv[1]
    except IndexError:
        tname = 'html'

    try:
        target = eval(tname)
    except NameError:
        print 'ERROR: invalid target name %r' % tname
        sys.exit(1)

    target()
