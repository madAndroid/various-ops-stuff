#!/usr/bin/python

import os, sys, datetime, stat, time, optparse, re

from stat import *
from fnmatch import fnmatch
from glob import glob

foundfiles = []
dirlist = []

__version__ = '0.0.1'

### File finder:

def find_all_files(search_location):
   
    file_list = []
    dir_list = []
    abs_path_list = []
    tmp_list = []

    for root, dirs, files in os.walk(search_location):
        for subdir in dirs:
            dir_list.append(os.path.join(root, subdir))
        for filename in files:
            abs_path_list.append(os.path.join(root, filename))
            file_list.append(filename)

    all_files = list(set(file_list))
    all_dirs_list = list(set(dir_list))
    all_files_abs = list(set(abs_path_list))

    return all_files, all_files_abs, all_dirs_list


### File Operations:

def include_files(all_files, inc_files):

    inc_list = []
    inc_list1 = []
    inc_list2 = []

    if len(inc_files) == 1:
        for fn in all_files:
            if inc_files[0] in os.path.basename(fn.lower()):
                inc_list.append(fn)
    elif len(inc_files) == 2:
        for fn in all_files:
            if inc_files[0] in os.path.basename(fn.lower()):
                inc_list1.append(fn)
        for fn in all_files:
            if inc_files[1] in os.path.basename(fn.lower()):
                inc_list2.append(fn)
        inc_list = set(inc_list1) & set(inc_list2) 
    else: 
        print "only two search terms allowed"

    final_list = list(inc_list)
    return final_list


def exclude_files(all_files, exc_files):

    exc_list = []
    exc_list1 = []
    exc_list2 = []

    if len(exc_files) == 1:
        for fn in all_files:
            if exc_files[0] in os.path.basename(fn.lower()):
                exc_list.append(fn)
    elif len(exc_files) == 2:
        for fn in all_files:
            if exc_files[0] in os.path.basename(fn.lower()):
                exc_list1.append(fn)
        for fn in all_files:
            if exc_files[1] in os.path.basename(fn.lower()):
                exc_list2.append(fn)
        exc_list = set(exc_list1) | set(exc_list2) 
    else:
        print "only two search terms allowed"

    final_list =  list(set(exc_list))
    return final_list


### Directory operations:

def include_dirs(all_dirs, inc_dirs):

    inc_list = []
    inc_list1 = []
    inc_list2 = []

    if len(inc_dirs) == 1:
        for dn in all_dirs:
            if inc_dirs[0] in dn.lower():
                inc_list.append(dn)
    elif len(inc_dirs) == 2:
        for dn in all_dirs:
            if inc_dirs[0] in dn.lower():
                inc_list1.append(dn)
        for dn in all_dirs:
            if inc_dirs[1] in dn.lower():
                inc_list2.append(dn)
        inc_list = set(inc_list1) & set(inc_list2) 
    else: 
        print "only two search terms allowed"

    final_list = list(inc_list)
    return final_list

def exclude_dirs(all_dirs, exc_dirs):

    exc_list = []
    exc_list1 = []
    exc_list2 = []

    if len(exc_dirs) == 1:
        for dn in all_dirs:
            if exc_dirs[0] in dn.lower():
                exc_list.append(dn)
    elif len(exc_dirs) == 2:
        for dn in all_dirs:
            if exc_dirs[0] in dn.lower():
                exc_list1.append(dn)
        for dn in all_dirs:
            if exc_dirs[1] in dn.lower():
                exc_list2.append(dn)
        exc_list = set(exc_list1) | set(exc_list2) 
    else:
        print "only two search terms allowed"

    final_list =  list(exc_list)
    return final_list


### File Size Operations:

#def check_file_size(filtered_files, size):
#    
#    pos_check = '+'
#    neg_check = '-'
#    if pos_check in size:
#        size_check = '>' 
#        size_int = size.strip("+")
#    else:
#        size_check = '<' 
#        size_int = size.strip("-")
#
#    byte_tag = size.lower()[-1:]
#    mb_tag = 'm'
#    kb_tag = 'k'
#    size_tmp = size_int.lower()
#    if mb_tag in byte_tag:
#        size_int = size_tmp.strip("m")
#    else:
#        size_int = size_tmp.strip("k") 
#
#    print "byte_tag:  " + byte_tag
#    print "size_check:  " + size_check
#    print "size_int:  " + size_int
#
#    print "checking"
#    time.sleep(2)
#
#    if size_check == '>':
#        for file in filtered_files:
#            try:
#                fstat = os.stat(file)
#                fsize = fstat.st_size
#                print file
#                print fsize
#                time.sleep(2)
#                if fsize > size_int:
#                    print "larger than"
#                else:
#                    print "smaller than"
#            except OSError, err:
#                print "couldn't access file %s" % (file)
#    else:
#        for file in filtered_files:
#            try:
#                fstat = os.stat(file)
#                fsize = fstat.st_size
#                print file
#                print fsize
#                time.sleep(2)
#                if fsize < size_int:
#                    print "smaller than"
#                else:
#                    print "larger than"
#            except OSError, err:
#                print "couldn't access file %s" % (file)
#
#    if byte_tag == kb_tag:
#        byte_size = size.strip
#
###
### Main check Function:
###

def run_check(path, check_size, check_time, inc_files, exc_files, inc_dirs, exc_dirs):

    (file_list, file_list_abs, dir_list) = find_all_files(path)

    if inc_files and exc_files is not None:
        inc_list = include_files(file_list_abs, inc_files)
        exc_list = exclude_files(file_list_abs, exc_files)
        final_file_list = set_operations(inc_list, exc_list)

    elif inc_files is not None:
        inc_list = include_files(file_list_abs, inc_files)
        final_file_list = inc_list

    elif exc_files is not None:
        exc_list = exclude_files(file_list_abs, exc_files)
        final_file_list = list(set(file_list_abs) - set(exc_list))

    else:
        final_file_list = file_list_abs


    if inc_dirs and exc_dirs is not None:
        inc_list = include_dirs(dir_list, inc_dirs)
        exc_list = exclude_dirs(dir_list, exc_dirs)
        final_dir_list = set_operations(inc_list, exc_list)

    elif inc_dirs is not None:
        inc_list = include_dirs(dir_list, inc_dirs)
        final_dir_list = inc_list

    elif exc_dirs is not None:
        exc_list = exclude_dirs(dir_list, exc_dirs)
        final_dir_list = list(set(dir_list) - set(exc_list))

    else:
        final_dir_list = dir_list

    final_dir_list.sort()
    final_file_list.sort()

    filter_dir = []
    final_files = []

    for fn in final_file_list:
        filter_dir.append(os.path.dirname(fn))

    final_dirs = set(filter_dir) & set(final_dir_list) 

    print final_dirs
    print final_file_list

    for file in final_file_list:
        for dir in final_dirs:
            print dir
            if dir in final_file_list:
                print file
                final_files.append(file)
    
    final_list = final_files
    
    num_items = len(final_list)

    if check_size is not None:
        check_file_size(final_list, check_size)

    for f in final_list:
        print "%s" %(f) 
        time.sleep(0.2)

    print "num items: %s" %(num_items)


### Helpers:
    
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


def set_operations(inclusions, exclusions):

    inclusions_set = set(inclusions)
    exclusions_set = set(exclusions)
    
    final_set = inclusions_set - exclusions_set

    return list(final_set)


### MAIN:

if __name__ == "__main__":
    import optparse
    parser = optparse.OptionParser(
        usage= """
            Nagios multi function file check
            """,
        version=__version__)
    parser.add_option("-p", "--path",
        help="path to check under - top level\n")
    parser.add_option("-e", "--exclude_files",
        help="a file pattern to exclude (string only - no regex)\n")
    parser.add_option("-i", "--include_files",
        help="a file pattern to include (string only - no regex)\n")
    parser.add_option("-E", "--exclude_dirs",
        help="a directory pattern to exclude (string only - no regex)\n")
    parser.add_option("-I", "--include_dirs",
        help="a directory pattern to include (string only - no regex)\n")
    parser.add_option("-m", "--mtime",
        help="last modified time\n")
    parser.add_option("-s", "--size",
        help="file size to check against\n")

    (options, args) = parser.parse_args()

    if not options.path:
        parser.error("\tThe -p (--path) option is required\n")

    if not os.path.exists(options.path):
        parser.error("Check path: '%s' does not exist" % options.path)

#    if not options.mtime or options.size:
#        parser.error("No attribute specified - we need something to check - mtime or size is required")

    if options.mtime and options.size:
        parser.error("Unfortunately you can't check both size and time at once (just yet)\n")

    if options.exclude_files:
        _exclude_files = [f.strip() for f in options.exclude_files.split(',')]
    else: 
        _exclude_files = None

    if options.include_files:
        _include_files = [f.strip() for f in options.include_files.split(',')]
    else: 
        _include_files = None

    if options.exclude_dirs:
        _exclude_dirs = [f.strip() for f in options.exclude_dirs.split(',')]
    else: 
        _exclude_dirs = None

    if options.include_dirs:
        _include_dirs = [f.strip() for f in options.include_dirs.split(',')]
    else: 
        _include_dirs = None

    if options.mtime:
        _check_time = [f.strip() for f in options.mtime.split(',')]
    else:
        _check_time = None

    if options.size:
        _check_size = options.size
    else:
        _check_size = None

    run_check(options.path, _check_size, _check_time, _include_files, _exclude_files, _include_dirs, _exclude_dirs)

