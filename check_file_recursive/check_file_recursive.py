#!/usr/bin/python

import os, sys, datetime, stat, time
from stat import *
from fnmatch import fnmatch
from glob import glob

foundfiles = []
dirlist = []
filelist = []

for root, dirs, files in os.walk('/home/andrew/Dropbox'):
#    print root,
#    print dirs,
#    print files
    for subdir in dirs:
#        dirlist.append(subdir)
#        print os.path.join(root, subdir)
        dirlist.append(os.path.join(root, subdir))

    for filename in files:
        filelist.append(os.path.join(root, filename))

#print dirlist
#print filelist

#foundfiles = glob("/home/andrew/*/*d*")
foundfiles = filelist

#print foundfiles

for dir in dirlist:
#    print dir
    if 'Clients' in dir:
        for file in foundfiles:
            if 'png' in file:
                filestat = os.stat(file)
                filesize = filestat.st_size * 1024
                print file
                time.sleep(1)
                print filesize, 'K'

