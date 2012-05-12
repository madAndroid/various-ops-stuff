#!/usr/bin/python

import os, sys, datetime, stat, time
from stat import *
from fnmatch import fnmatch
from glob import glob

foundfiles = []
dirlist = []
filelist = []

def convert_bytes(bytes):
    bytes = float(bytes)
    if bytes >= 1099511627776:
        terabytes = bytes / 1099511627776
        size = '%.2fT' % terabytes
    elif bytes >= 1073741824:
        gigabytes = bytes / 1073741824
        size = '%.2fG' % gigabytes
    elif bytes >= 1048576:
        megabytes = bytes / 1048576
        size = '%.2fM' % megabytes
    elif bytes >= 1024:
        kilobytes = bytes / 1024
        size = '%.2fK' % kilobytes
    else:
        size = '%.2fb' % bytes
    return size


for root, dirs, files in os.walk('/opt/scribe/storage'):
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

matcheddir = []

for file in foundfiles:
    print file, '\nnot in'
    time.sleep(0.02)
    if 'syslog' in file:
        print file 
        time.sleep(0.1)
        if '_current' in file:
            print file
            fstat = os.stat(file)
            fsize = fstat.st_size
            if fsize > 0:
                truesize = convert_bytes(fsize)
                print truesize
            else:
                print '[empty]'


#        matcheddir.append(dir)


#print matcheddir

#for dir in targetdir:
#    for file in foundfiles:
#            if file in dir:
#                print dir
#                print file
#
##        if 'Clients' in dir and 'png' in foundfiles:
##        for file in foundfiles:
#                filestat = os.stat(file)
#                filesize = filestat.st_size * 1024
##                print file
#                time.sleep(1)
#                print filesize, 'K'
#
