#!/usr/bin/python

import os, sys, datetime, stat
import shutil, time, optparse, re
import logging

from stat import *
from fnmatch import fnmatch
from glob import glob
from subprocess import Popen, PIPE, call

""" Script to check multiple aspects of files and directories

    :var LOG_LEVEL: This is the default logging level.  Here are suitable values:
    - 10 = DEBUG
    - 20 = INFO
    - 30 = WARNING
    - 40 = ERROR
    - 50 = CRITICAL

    :change: B{0.0.1} - 2012-05-21
    - Checking list of files by name, with filters on file and directory names
    """
__author__ = "Andrew Stangl"
__date__ = "2012-05-15"
__version__ = "0.0.1"

# Exit statuses recognized by Nagios
UNKNOWN = -1
OK = 0
WARNING = 1
CRITICAL = 2

LOG_LEVEL = 20
logging.basicConfig(
    format="%(asctime)s (%(filename)s, %(funcName)s, %(lineno)d) "
    "[%(levelname)8s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=LOG_LEVEL)
_logger = logging.getLogger()

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


def filter_files(file_list_abs, dir_list, inc_files, exc_files, inc_dirs, exc_dirs):

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

    final_file_list.sort()
    final_file_set = set(final_file_list)

    tmp_final_files = []

    if inc_dirs and exc_dirs is not None:
        inc_list = include_dirs(dir_list, inc_dirs)
        exc_list = exclude_dirs(dir_list, exc_dirs)
        final_dir_list = set_operations(inc_list, exc_list)
        for tmp_file in list(final_file_set):
            for tmp_dir in final_dir_list:
                if tmp_dir in os.path.dirname(tmp_file):
                    _logger.info("File ='%s' found", tmp_file)
                    tmp_final_files.append(tmp_file)
        final_files = final_file_set & set(tmp_final_files)

    elif inc_dirs is not None:
        inc_list = include_dirs(dir_list, inc_dirs)
        final_dir_list = set(inc_list)
        for tmp_file in list(final_file_set):
            for tmp_dir in final_dir_list:
                if tmp_dir in os.path.dirname(tmp_file):
                    _logger.info("File ='%s' found", tmp_file)
                    tmp_final_files.append(tmp_file)
        final_files = final_file_set & set(tmp_final_files)

    elif exc_dirs is not None:
        exc_list = exclude_dirs(dir_list, exc_dirs)
        final_dir_list = set(exc_list)
        for tmp_file in list(final_file_set):
            for tmp_dir in final_dir_list:
                if tmp_dir in os.path.dirname(tmp_file):
                    _logger.info("File ='%s' found", tmp_file)
                    tmp_final_files.append(tmp_file)
        final_files = final_file_set - set(tmp_final_files)

    else:
        final_files = final_file_list
    
    final_list = list(final_files)
    final_list.sort()
    set(final_list)

    num_items = len(final_list)
    _logger.info("'%s' Files found", num_items)

    return final_list
##
### File Operations:
##
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
        _logger.error("Only two inclusions allowed!")
        sys.exit(1)

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
        _logger.error("Only two exclusions allowed!")
        sys.exit(1)

    final_list =  list(set(exc_list))
    return final_list


### Directory operations:
##
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
        _logger.error("Only two inclusions allowed!")
        sys.exit(1)

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
        _logger.error("Only two exclusions allowed!")
        sys.exit(1)

    final_list =  list(exc_list)
    return final_list


### File Size Operations:

def check_file_size(filtered_files, size):
    
    pos_check = '+'
    neg_check = '-'

    if pos_check in size:
        size_check = '>' 
        size_int = size.strip("+")
        threshold = 'above'
    elif neg_check in size:
        size_check = '<' 
        size_int = size.strip("-")
        threshold = 'below'
    else:
        _logger.error("no modifier supplied - need to specify '+' or '-' ")
        sys.exit(1)

    if size_int.isdigit():
        byte_tag = 'k'
    else:
        byte_tag = size.lower()[-1:]

    mb_tag = 'm'
    kb_tag = 'k'
    size_tmp = size_int.lower()
    if mb_tag in byte_tag:
        size_int = int(size_tmp.strip("m")) * 1024 * 1024
    elif kb_tag in byte_tag:
        size_int = int(size_tmp.strip("k")) * 1024
    else:
        size_int = int(size_tmp.strip("k"))
    
    _logger.debug("Byte tag: %s size_check: %s size_int: %s " 
        %(byte_tag, size_check, size_int))

    _logger.debug("Checking sizes ...")

    target_files = []

    filtered_list = []
    filtered_list = list(filtered_files)

    filtered_list.sort() 

    if size_check == '>':
        for file in filtered_list:
            try:
                fstat = os.stat(file)
                fsize = fstat.st_size
                if fsize > size_int:
                    _logger.debug("File: %s is larger than size: %s " %(file,size_tmp))
                    target_files.append(file)
                else:
                    _logger.debug("File: %s is smaller than size: %s " %(file,size_tmp))
            except OSError, err:
                _logger.error("Cannot access file: %s " %(file))
    else:
        for file in filtered_list:
            try:
                fstat = os.stat(file)
                fsize = fstat.st_size
                if fsize < size_int:
                    _logger.debug("File: %s is smaller than size: %s " %(file,size_tmp))
                    target_files.append(file)
                else:
                    _logger.debug("File: %s is larger than size: %s " %(file,size_tmp))
            except OSError, err:
                _logger.error("Cannot access file: %s " %(file))

    check_list = []
    target_list = list(set(target_files))
    target_list.sort()
    
    if len(target_list) > 0:
        for f in target_list:
            _logger.debug("File: %s is %s the threshold of size: %s " %(f,threshold,size_tmp))
        _logger.info("%s files are %s the threshold of size: %s " %(len(target_list),threshold,size_tmp))

    return target_list

## File Age Operations:
def check_file_age(filtered_files, age):

    afr_check = '+'
    bfr_check = '-'

    if afr_check in age:
        age_check = '>' 
        age_int = age.strip("+")
        threshold = 'after'
        age_ident = 'older'
    elif bfr_check in age:
        age_check = '<' 
        age_int = age.strip("-")
        threshold = 'before'
        age_ident = 'younger'
    else:
        _logger.error("no modifier supplied - need to specify '+' or '-' ")
        sys.exit(1)

    if age_int.isdigit():
        time_tag = 's'
    else:
        time_tag = age.lower()[-1:]

    sec_tag = 's'
    min_tag = 'm'
    hrs_tag = 'h'
    day_tag = 'd'

    age_tmp = age_int.lower()

    if sec_tag in time_tag:
        age_int = int(age_tmp.strip("s"))
        _logger.debug("Checking file ages %s than... %s " %(age_ident, convert_seconds(age_int)))
    elif min_tag in time_tag:
        age_int = int(age_tmp.strip("m")) * 60
        _logger.debug("Checking file ages %s than... %s " %(age_ident, convert_seconds(age_int)))
    elif hrs_tag in time_tag:
        age_int = int(age_tmp.strip("h")) * 60 * 60
        _logger.debug("Checking file ages %s than... %s " %(age_ident, convert_seconds(age_int)))
    else:
        age_int = int(age_tmp.strip("d")) * 60 * 60 * 24
        _logger.debug("Checking file ages %s than... %s " %(age_ident, convert_seconds(age_int)))
   
    _logger.debug("Age tag: %s age_check: %s age_int: %s " 
        %(time_tag, age_check, age_int))

    _logger.debug("Checking file ages ...")

    target_files = []

    filtered_list = []
    filtered_list = list(filtered_files)

    filtered_list.sort() 

    if age_check == '>':
        for file in filtered_list:
            try:
                fstat = os.stat(file)
                fmtime = fstat.st_mtime
                fmage = time.time() - fmtime
                _logger.debug("Current file: %s was modified %s ago" %(file, convert_seconds(fmage)))
                if fmage > age_int:
                    _logger.debug("File: %s is older than: %s " %(file,age_tmp))
                    target_files.append(file)
                else:
                    _logger.debug("File: %s is younger than: %s " %(file,age_tmp))
            except OSError, err:
                _logger.error("Cannot access file: %s " %(file))
    else:
        for file in filtered_list:
            try:
                fstat = os.stat(file)
                fmtime = fstat.st_mtime
                fmage = time.time() - fmtime
                _logger.debug("Current file: %s was modified %s ago" %(file, convert_seconds(fmage)))
                if fmage < age_int:
                    _logger.debug("File: %s is younger than: %s " %(file,age_tmp))
                    target_files.append(file)
                else:
                    _logger.debug("File: %s is older than: %s " %(file,age_tmp))
            except OSError, err:
                _logger.error("Cannot access file: %s " %(file))

    check_list = []
    target_list = list(set(target_files))
    target_list.sort()
    
    if len(target_list) > 0:
        for f in target_list:
            _logger.debug("File: %s is %s the threshold of age: %s " %(f,threshold,age_tmp))
        _logger.info("%s files are %s the threshold of age: %s " %(len(target_list),threshold,age_tmp))

    return target_list

def check_if_empty(path):

    file_list = []
    dir_list = []
    abs_path_list = []
    tmp_list = []

    for root, dirs, files in os.walk(path):
        for subdir in dirs:
            dir_list.append(os.path.join(root, subdir))
        for filename in files:
            abs_path_list.append(os.path.join(root, filename))
            file_list.append(filename)

    if file_list:
        _logger.debug("Directory is not empty!!")
        print 'CRITICAL - Directory %s is not empty!! - %s' %(path, file_list)
        raise SystemExit, CRITICAL
    else:
        _logger.debug("Directory is empty")
        print 'OK - Directory %s is empty' %(path)
        raise SystemExit, OK

###
### Main check Function:
###

def run_check(path, check_size, check_time, inc_files, exc_files, inc_dirs, exc_dirs, empty_dir=False, reverse_check=False):

    if empty_dir:
        check_if_empty(path)

    if os.path.isfile(path):
        ready_list = [path,] 
    else:
        (file_list, file_list_abs, dir_list) = find_all_files(path)
        ready_list = set(filter_files(file_list_abs, dir_list, inc_files, exc_files, inc_dirs, exc_dirs))

    if check_size and check_time is not None:
        file_size_list = check_file_size(ready_list, check_size)
        file_age_list = check_file_age(ready_list, check_time)
        final_check_list = set(file_size_list) & set(file_age_list)
    elif check_size is not None:
        final_check_list = check_file_size(ready_list, check_size)
    else:
        final_check_list = check_file_age(ready_list, check_time)

    final_check_list = list(final_check_list)
    final_check_list.sort()
    num_items = len(final_check_list)
    for f in final_check_list:
        _logger.debug("'%s' found", f)
    _logger.debug("'%s' Files found", num_items)

    if reverse_check:
        if final_check_list:
            _logger.debug("All checks passed")
            print 'OK - all checks passed' 
            raise SystemExit, OK
        else: 
            _logger.debug("One or more checks failed!")
            print 'CRITICAL - One or more checks failed !! - No file(s) within threshold' %(num_items)
            raise SystemExit, CRITICAL
    
    if final_check_list:
        _logger.debug("One or more checks failed!")
        print 'CRITICAL - One or more checks failed !! - %s file(s) outside of threshold: %s' %(num_items,final_check_list)
        raise SystemExit, CRITICAL
    else: 
        _logger.debug("All checks passed")
        print 'OK - all checks passed' 
        raise SystemExit, OK


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


def convert_seconds(seconds):
    seconds = int(seconds)
    if seconds >= 86400:
        days = seconds / 86400
        age = '%d days' % days
    elif seconds >= 3600:
        hours = seconds / 3600
        age = '%d hours' % hours
    elif seconds >= 60:
        minutes = seconds / 60
        age = '%d minutes' % minutes
    else:
        age = '%d seconds' % seconds
    return age


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
    parser.add_option("-l", "--log-level",
        help="Adjust the logging level. Suitable values include "
        "10 (DEBUG), 20 (INFO), 30 (WARNING), 40 (ERROR), 50 (CRITICAL). "
        "Default=%d" % LOG_LEVEL)
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
    parser.add_option("-d", "--empty-dir", action="store_true",
        help="Check if directory specified is empty\n")
    parser.add_option("-r", "--reverse_check", action="store_true",
        help="Reverse logic of check, to check inverse of requirements\n")

    parser.set_defaults(log_level=str(LOG_LEVEL))

    (options, args) = parser.parse_args()

    _logger.setLevel(int(options.log_level))

    if not options.path:
        parser.error("\tThe -p (--path) option is required\n")
    if not os.path.exists(options.path):
        parser.error("Check path: '%s' does not exist" % options.path)

    if not options.size and not options.mtime and not options.empty_dir:
        parser.error("\n\tNo attribute specified - we need something to check - time / size / emptydir\n")

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
        _check_time = options.mtime
    else:
        _check_time = None
    if options.reverse_check:
        _reverse = True
    else:
        _reverse = False

    if options.size:
        _check_size = options.size
    else:
        _check_size = None
    if options.empty_dir:
        _empty_dir = True
    else:
        _empty_dir = False

    run_check(options.path, _check_size, _check_time, _include_files, _exclude_files, _include_dirs, _exclude_dirs, _empty_dir, _reverse)

