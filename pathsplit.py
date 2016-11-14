#!/usr/bin/env python

import sys
splitstring='/'
tempstring  = sys.argv[1]
if len(sys.argv) == 3 :
    splitstring =sys.argv[2]

pathlist = tempstring.split(splitstring)
print pathlist[-1]

