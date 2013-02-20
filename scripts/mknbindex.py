#!/usr/bin/env python
"""Simple script to auto-generate the index of notebooks in a given directory.
"""

import glob
import urllib

notebooks = sorted(glob.glob('*.ipynb'))

tpl = ( '* [{0}](http://nbviewer.ipython.org/url/github.com/cocotools/CoCoTools/'
        'raw/master/examples/{1})' )

idx = [ 
"""# A collection of Notebooks for using CoCoTools

The following notebooks showcase how to use CoCoTools interactively for
querying the CoCoMac connectivity database.
"""]

idx.extend(tpl.format(nb.replace('.ipynb',''), urllib.quote(nb)) 
           for nb in notebooks)

with open('README.md', 'w') as f:
    f.write('\n'.join(idx))
    f.write('\n')
