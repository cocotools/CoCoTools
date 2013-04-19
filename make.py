#!/usr/bin/env python
"""Script to run tests with CI. May do more in the future
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
	
def tests():
	"""Run tests"""
	sh('python cocotools/test/test_*.py')