#!/usr/bin/python

import os, sys, datetime, stat, time, optparse

from stat import *
from fnmatch import fnmatch
from glob import glob

foundfiles = []
dirlist = []
filelist = []

#parser = OptionParser()
#parser.add_option("-f", "--file", dest="filename",
#                  help="write report to FILE", metavar="FILE")
#parser.add_option("-q", "--quiet",
#                  action="store_false", dest="verbose", default=True,
#                  help="don't print status messages to stdout")
#
#(options, args) = parser.parse_args()

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
    for subdir in dirs:
        dirlist.append(os.path.join(root, subdir))

    for filename in files:
        filelist.append(os.path.join(root, filename))

all_files = filelist
all_dirs = dirlist

matched_dir = []
exc_files = []

filtered_files = []

for file in all_files:
    if 'syslog' in file:
        filtered_files.append(file)

#        if '_current' in file:
#            print file
#            fstat = os.stat(file)
#            fsize = fstat.st_size
#            if fsize > 0:
#                truesize = convert_bytes(fsize)
#                print truesize
#            else:
#                print '[empty]'

print filtered_files
print "[pause 1]"
time.sleep(2)

file_set = set(all_files)
dir_set = set(all_dirs)

print file_set
print "[pause 2]"
time.sleep(2)
print dir_set

inc_set = file_set.intersection(filtered_files)

print "[pause 3]"
time.sleep(2)
print inc_set

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
