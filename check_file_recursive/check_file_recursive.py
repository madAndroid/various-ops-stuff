#!/usr/bin/python

import os, sys, datetime, stat, time, optparse

from stat import *
from fnmatch import fnmatch
from glob import glob

foundfiles = []
dirlist = []
filelist = []

search_here = '/opt/scribe/storage'
narrow_search = 'current'
narrow_search_more = 'syslog'
exclude_this = 'admin'
exclude_this_too = 'client'

#parser = OptionParser()
#parser.add_option("-f", "--file", dest="filename",
#                  help="write report to FILE", metavar="FILE")
#parser.add_option("-q", "--quiet",
#                  action="store_false", dest="verbose", default=True,
#                  help="don't print status messages to stdout")
#
#(options, args) = parser.parse_args()

def find_all_files(search_location, sub_search = None):
    for root, dirs, files in os.walk(search_location):
        for subdir in dirs:
            dirlist.append(os.path.join(root, subdir))
        for filename in files:
            filelist.append(os.path.join(root, filename))

    all_files = filelist
    file_set = set(all_files)
    all_dirs = dirlist
    dir_set = set(all_dirs)
    #return file_set, dir_set
    return file_set

### the following are filter functions:

def include_files(all_files, inc_files1, inc_files2 = None):
    included_list = []
    included_list2 = []
    print "search_term:" + inc_files1
    if inc_files2:
        print "another filter:" + inc_files2
    time.sleep(2)

    # first search term
    for file in all_files:
        if inc_files1 in file:
            included_list.append(file)

    included_set = set(included_list)

    # If we need another search term:
    if inc_files2 is not None:
        for file2 in all_files:
            if inc_files2 in file2:
                included_list2.append(file2)
    try:
        included_list2
    except NameError:
        print ""
    else:
        included_set2 = set(included_list2)
        final_set = included_set & included_set2
#        for fs in final_set:
#            print fs
#            time.sleep(1)
        return final_set
    
#    for fs in included_set:
#        print fs
#        time.sleep(1)
#
    final_set = included_set
    return final_set

def exclude_files(all_files, exc_files1, exc_files2 = None):
    excluded_list = []
    excluded_list2 = []
    print "exclude term:" + exc_files1
    if exc_files2:
        print "another exclusion:" + exc_files2
    time.sleep(2)

    # first exclusion term
    for file in all_files:
        if exc_files1 in file:
            excluded_list.append(file)

    excluded_set = set(excluded_list)

    # If we need another exclusion:
    if exc_files2 is not None:
        for file2 in all_files:
            if exc_files2 in file2:
                excluded_list2.append(file2)
    else:
#        for fs in excluded_set:
#            print fs
#            time.sleep(1)

        final_set = excluded_set
        return final_set

    try:
        excluded_list2
    except NameError:
        print ""
    else:
        excluded_set2 = set(excluded_list2)
        final_set = excluded_set & excluded_set2
#        for fs in final_set:
#            print fs
#            time.sleep(1)
        return final_set
  

#def filter_files(all_files, search_term = None, exclude_these1 = None, exclude_these2 = None):
#    filtered_files = []
#    excluded_files = []
#    excluded_files2 = []
#    print "search_term:" + search_term 
#    print "exclusions:" + exclude_these1
#    if exclude_these2:
#        print "more exclusions:" + exclude_these2
#    time.sleep(2)
#
#    for file in all_files:
#        if search_term in file:
#            filtered_files.append(file)
#    for exc_file in all_files:
#        if exclude_these1 in exc_file:
#            excluded_files.append(exc_file)
#    if exclude_these2 is not None:
#        for exc_file2 in all_files:
#            if exclude_these2 in exc_file2:
#                excluded_files2.append(exc_file2)
#
#    filtered_set = set(filtered_files)
#    excluded_set = set(excluded_files)
#    if excluded_files2:
#        excluded_set2 = set(excluded_files2)
#
#    final_set = filtered_set - excluded_set
#    try:
#        excluded_set2
#    except NameError:
#        print ""
#    else:
#        final_set = final_set - excluded_set2
#
#    print "next, final set"
#    final_list = list(final_set)
#    for file in final_list:
#        print file
#        time.sleep(0.2)
#    return final_list

#matched_dir = []
#exc_files = []

file_list = {}
final_files = {}
final_files2 = {}

file_list = find_all_files(search_here)

inclusions_set = include_files(file_list, narrow_search, narrow_search_more)
exclusions_set = exclude_files(file_list, exclude_this)

print "Inclusions:"
for file in inclusions_set:
    print file
#    time.sleep(.1)

print "Exclusions:"
for file in exclusions_set:
    print file
#    time.sleep(.1)

return_set = inclusions_set - exclusions_set

print "Final set:"
for file in return_set:
    print file
#    time.sleep(.5)

#for f in final_files:
#    print f
#    time.sleep(0.2)
#
#        if '_current' in file:
#            print file
#            fstat = os.stat(file)
#            fsize = fstat.st_size
#            if fsize > 0:
#                truesize = convert_bytes(fsize)
#                print truesize
#            else:
#                print '[empty]'

#print filtered_files
#print "[pause 1]"
#time.sleep(2)
#
#file_set = set(all_files)
#dir_set = set(all_dirs)
#
#print file_set
#print "[pause 2]"
#time.sleep(2)
#print dir_set
#
#inc_set = file_set.intersection(filtered_files)
#
#print "[pause 3]"
#time.sleep(2)
#print inc_set
#
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


