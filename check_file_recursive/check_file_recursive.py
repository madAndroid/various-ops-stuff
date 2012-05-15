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

__version__ = '0.0.1'

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

#matched_dir = []
#exc_files = []

#file_list = {}
#final_files = {}
#final_files2 = {}
#
#file_list = find_all_files(search_here)
#
#inclusions_set = include_files(file_list, narrow_search, narrow_search_more)
#exclusions_set = exclude_files(file_list, exclude_this)

#print "Inclusions:"
#for file in inclusions_set:
#    print file
##    time.sleep(.1)
#
#print "Exclusions:"
#for file in exclusions_set:
#    print file
##    time.sleep(.1)
#
#return_set = inclusions_set - exclusions_set
#
#print "Final set:"
#for file in return_set:
#    print file
##    time.sleep(.5)
#
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

def run_check(path, check_size, check_time, _filter, _exclude):

    file_list = find_all_files(path)

    inclusions_set = include_files(file_list, _filter)
    exclusions_set = exclude_files(file_list, _exclude)

    final_set = inclusions_set - exclusions_set
    print final_set
    

if __name__ == "__main__":
    import optparse
    parser = optparse.OptionParser(
        usage= """
            Nagios multi function file check
            """,
        version=__version__)
    parser.add_option("-p", "--path",
        help="path to check under - top level")
    parser.add_option("-e", "--exclude",
        help="a pattern to exclude (string only - no regex)")
    parser.add_option("-f", "--filter",
        help="a pattern to search for (string only - no regex)")
    parser.add_option("-m", "--mtime",
        help="last modified time")
    parser.add_option("-s", "--size",
        help="file size to check against")

    (options, args) = parser.parse_args()

    if not options.path:
        parser.error("The -p (--path) option is required")

    if not os.path.exists(options.path):
        parser.error("Check path: '%s' does not exist" % options.path)

#    if not options.mtime or options.size:
#        parser.error("No attribute specified - we need something to check - mtime or size is required")
#
    if options.mtime and options.size:
        parser.error("Unfortunately you can't check both size and time at once (just yet)")

    if options.exclude:
        _exclude = [f.strip() for f in options.exclude.split(',')]
    else: 
        _exclude = False

    if options.filter:
        _filter = [f.strip() for f in options.filter.split(',')]
    else: 
        _filter = False

    if options.mtime:
        _check_time = options.mtime
    else:
        _check_time = False

    if options.size:
        _check_size = options.size
    else:
        _check_size = False

    run_check(options.path, _check_size, _check_time, _filter, _exclude)

