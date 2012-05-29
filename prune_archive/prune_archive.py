#!/usr/bin/env python 
import os, time, sys
import logging
import re
import shutil
import signal
import mimetypes
import filecmp
import socket
from lockfile import FileLock

from subprocess import Popen, PIPE, call
import pdb
import hashlib
from functools import partial

_logfile = './' + self + 'log' + self + '.log'
_lockfile = './' + self + '.IS_RUNNING'
_mail_host = 'localhost'

LOG_LEVEL = 30

_logger = logging.getLogger()

_ch = logging.StreamHandler()
_fh = logging.handlers.RotatingFileHandler(_logfile, backupCount=7)
_mh = logging.handlers.SMTPHandler(
    _mail_host,
    fromaddr=_alerts_from,
    toaddrs=_alerts_to,
    subject='Backup_to_S3.py script Failure')
 
ch_formatter = logging.Formatter('%(asctime)s, %(name)-12s: [%(levelname)8s] %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
fh_formatter = logging.Formatter('%(asctime)s, %(name)-12s: [%(levelname)8s] %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
mh_formatter = logging.Formatter('%(asctime)s, : [%(levelname)4s] %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
 
_ch.setFormatter(ch_formatter)
_mh.setFormatter(mh_formatter)
_fh.setFormatter(fh_formatter)
 
_logger.addHandler(_fh)
_logger.addHandler(_ch)
_logger.addHandler(_mh)

## Locates all files given as only argument to script (rest are options)
def get_all_files(_storage_loc):

    dirlist = []
    filelist = []

    for root, dirs, files in os.walk(_storage_loc):
        for subdir in dirs:
            dirlist.append(os.path.join(root, subdir))
        for filename in files:
            filelist.append(os.path.join(root, filename))

    found_files = set(filelist)
    return list(found_files)

## returns a list of open files, for exclusion:
def find_open_files(_storage_loc):
   
    output = []
    p1 = Popen(["lsof +D " + _storage_loc ], shell=True, stdout=PIPE)
    output = p1.communicate()[0]

    tmp_list = output.split("\n")
    try:
        del tmp_list[0]
        del tmp_list[-1]
    except:
        _logger.debug("array elements don't exist - is the list zero length?")

    final_list = []
    for line in tmp_list:
        final_list.append(line.split()[-1])

    open_files = final_list
    return open_files

### Function to filter open files, as well as type specific files:
def filtered_list(_storage_loc, exclusions = None):
    
    file_list = get_all_files(_storage_loc)
    open_list = find_open_files(_storage_loc)

    ready_set = []
    ready_set = set(file_list) - set(open_list)

    ready_list = list(ready_set)

    exclusions is not None:
        exclude_set = set(exclude_files(ready_list, exclusions))
        ready_list = list(ready_set - exclude_set)
        ready_set = set(ready_list)
        ready_list.sort()
        return ready_list
    else
        ready_list.sort()
        return ready_list


### If any exclusions are specified, process them:
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
    else:
        print "only two search terms allowed"

    uniq_exc_files = list(set(excluded_list))

    final_list = uniq_exc_files
    return final_list


### prune the archived data, based on available space on the mountpoint
def prune_archive(f):

    fstat = os.stat(f)
    fmtime = int(fstat.st_mtime)
    time_now = int(time.time())
    time_diff = time_now - fmtime

    if time_diff > 604800:
        if os.path.exists(f):
            if not os.path.isdir(f):
                os.remove(f)
            else:
                os.rmdir(f)

def check_percentage(_storage_loc):

    mount_point = os.path.dirname(_storage_loc)

    if os.path.ismount(mount_point):
        disk_stat = os.statvfs(mount_point)

    total_size = int(disk_stat.f_blocks)
    free_size =  int(disk_stat.f_bavail)

    perc_free = 100 * int(free_size)/int(total_size)

    return perc_free


if __name__ == "__main__":
    import optparse
    parser = optparse.OptionParser(
        usage= """
            \n Copies files from file system path to S3 bucket
            \n\t example: backup_to_S3.py [SRC_PATH] -l [LOG_LEVEL] --dest s3://[BUCKET_NAME] --type [LOG_TYPE] --rate [RATE_LIMIT (in kb/s)]
            \n\t where LOG_TYPE is either 'text' or 'data'
            """,
        version=__version__)

    parser.add_option("-m", "--maxvol",
        help="Specify maximum volume to check against, based on available space")

    parser.add_option("-e", "--exclude",
        help="Specify any file name exclusions")

    parser.add_option("-a", "--age",
        help="Specify age threshold - files to delete")

    parser.set_defaults(log_level=str(LOG_LEVEL))

    (options, args) = parser.parse_args()

    _logger.setLevel(int(options.log_level))

    if options.log_level == '10':
        _fh.setLevel(logging.INFO)
        _ch.setLevel(logging.DEBUG)
        _mh.setLevel(logging.CRITICAL)
    elif options.log_level == '20':
        _fh.setLevel(logging.INFO)
        _ch.setLevel(logging.INFO)
        _mh.setLevel(logging.ERROR)
    elif options.log_level == '30':
        _fh.setLevel(logging.WARNING)
        _ch.setLevel(logging.WARNING)
        _mh.setLevel(logging.ERROR)
    elif options.log_level == '40':
        _fh.setLevel(logging.ERROR)
        _ch.setLevel(logging.ERROR)
        _mh.setLevel(logging.ERROR)
    else: 
        _fh.setLevel(logging.CRITICAL)
        _ch.setLevel(logging.CRITICAL)
        _mh.setLevel(logging.ERROR)

    if not args:
        parser.error("\tYou must specify a path to prune, as the first argument\n")
    if len(args) > 1:
        parser.error("\nYou can only specify one path to prune\n")
    if not os.path.exists(args[0]):
        parser.error("\nTarget '%s' does not exist\n" % args[0])

### Drop any trailing zero's in target path, if they exist:
    path_string = args[0]
    if path_string[-1] == "/":
        args[0] = path_string[0:-1]

    _storage_loc = args[0]

### Parse exclusions list
    _exclude = []
    if options.exclude:
        _exclude = [f.strip() for f in options.exclude.split(',')]
        _logger.debug("exclude=%s", ",".join(_exclude))
        if len(_exclude) > 2:
            parser.error("Only two exclusions allowed")
    else: 
        _exclude = None

### logging to file:
    if not os.path.exists(_logfile):
        _logger.error("log file does not exist!!")

### catchall exception:
    sys.excepthook = catchall_exceptions

### run the prune operation, with a lockfile in place to avoid multiple instances:

    lock = FileLock(_lockfile)

    if lock.is_locked():
        _logger.warn("Another instance of script is running!!")
        sys.exit(1)

    try:
        with lock:

            ## rotate our log file:
            _fh.doRollover()

            perc_free = check_percentage(_storage_loc)

            if perc_free =< options.maxvol:
                ## get a list of filtered files, with open files excluded, plus any (optional) exclusions
                src = filtered_list(_storage_loc, _exclude)
                
                for f in src:
                    prune_archive(f)

    except:
        _logger.exception("An uncaught exception occurred! with the following traceback:")
        sys.exit(1)

