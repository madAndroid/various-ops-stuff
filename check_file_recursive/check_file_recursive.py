#!/usr/bin/python

import os, sys, datetime, stat, time, optparse, re

from stat import *
from fnmatch import fnmatch
from glob import glob

foundfiles = []
dirlist = []

search_here = '/opt/scribe/storage'
narrow_search = 'current'
narrow_search_more = 'syslog'
exclude_this = 'admin'
exclude_this_too = 'client'

__version__ = '0.0.1'

def find_all_files(search_location, sub_search = None):

    file_list = []
    dir_list = []
    abs_path_list = []
    for root, dirs, files in os.walk(search_location):
        for subdir in dirs:
            dir_list.append(os.path.join(root, subdir))
        for filename in files:
            abs_path_list.append(os.path.join(root, filename))
            file_list.append(filename)
    
    all_files = file_list
    all_dirs = dir_list
    all_files_abs = abs_path_list

    return all_files, all_files_abs

### the following are filter functions:

def include_files(all_files, inc_files):

    included_list = []
    included_list1 = []
    included_list2 = []

    if len(inc_files) == 1:
        for file in all_files:
            if inc_files[0] in file:
                included_list.append(file)
    elif len(inc_files) == 2:
        for file in all_files:
            if inc_files[0] in file:
                included_list1.append(file)
        for file in all_files:
            if inc_files[1] in file:
                included_list2.append(file)
        included_list = set(included_list1) & set(included_list2) 
    else: 
        print "only two search terms allowed"

    uniq_inc_files = list(set(included_list))

    final_list = uniq_inc_files
    return final_list

def exclude_files(all_files, exc_files):

    excluded_list = []
    excluded_list1 = []
    excluded_list2 = []

    if len(exc_files) == 1:
        for file in all_files:
            if exc_files[0] in file:
                excluded_list.append(file)
    elif len(exc_files) == 2:
        for file in all_files:
            if exc_files[0] in file:
                excluded_list1.append(file)
        for file in all_files:
            if exc_files[1] in file:
                excluded_list2.append(file)
        excluded_list = set(excluded_list1) | set(excluded_list2) 
    elif len(exc_files) > 2:
        print "only two search terms allowed"
    else:
        return ""

    uniq_exc_files = list(set(excluded_list))

    final_list = uniq_exc_files
    return final_list

def check_file_size(filtered_files, size):

    print size

    pos_check = '+'
    neg_check = '-'
    
    if pos_check in size:
        size_check = '>' 
        size_int = int(size.strip('+'))
    else:
        size_check = '<' 
        size_int = int(size.strip('-'))

    print size_check
    print size_int

    if size_check == '>':
        for file in filtered_files:
            fstat = os.stat(file)
            fsize = fstat.st_size
            print file
            print fsize
            time.sleep(2)
            if fsize > size_int:
                print "larger than"
            else:
                print "smaller than"
    else:
        for file in filtered_files:
            fstat = os.stat(file)
            fsize = fstat.st_size
            print file
            print fsize
            time.sleep(2)
            if fsize < size_int:
                print "smaller than"
            else:
                print "larger than"


    
#    if size[0] != "+" or size[0] != "-":
#        print "you need to specify an operator"
#
#    print size[0]


#for f in final_files:
#    print f
#    time.sleep(0.2)
#
#        if '_current' in file:
#            print file
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

def run_check(path, check_size, check_time, include, exclude):

    (file_list, file_list_abs) = find_all_files(path)

    if include is not None:
        inclusions_list = include_files(file_list_abs, include)
        #print inclusions_set
    else:
        inclusions_list = []

    if exclude is not None: 
        exclusions_list = exclude_files(file_list_abs, exclude)
        #print exclusions_set
    else:
        exclusions_list = []

    if include and exclude is not None:
        final_list = set_operations(inclusions_list, exclusions_list)
    else:
        if include is not None:
            final_list = inclusions_list
        else: 
            final_list = list(set(file_list) - set(exclusions_list))

    final_list.sort()

    for file in final_list:
        print file

    num_items = len(final_list)

    if check_size is not None:
        check_file_size(final_list, check_size)

    print "num items:"
    print num_items

def set_operations(inclusions, exclusions):

    inclusions_set = set(inclusions)
    exclusions_set = set(exclusions)
    
    final_set = inclusions_set - exclusions_set

    return list(final_set)
   

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
    parser.add_option("-i", "--include",
        help="a pattern to include (string only - no regex)")
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

    if options.mtime and options.size:
        parser.error("Unfortunately you can't check both size and time at once (just yet)")

    if options.exclude:
        _exclude = [f.strip() for f in options.exclude.split(',')]
    else: 
        _exclude = None

    if options.include:
        _include = [f.strip() for f in options.include.split(',')]
    else: 
        _include = None

    if options.mtime:
        _check_time = [f.strip() for f in options.mtime.split(',')]
    else:
        _check_time = None

    if options.size:
        _check_size = options.size
    else:
        _check_size = None

    run_check(options.path, _check_size, _check_time, _include, _exclude)

