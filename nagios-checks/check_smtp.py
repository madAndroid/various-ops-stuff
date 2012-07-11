#!/usr/bin/python

import os, sys, datetime, stat
import smtplib, email.utils
import shutil, time, optparse, re
import logging

from email.mime.text import MIMEText

server = smtplib.SMTP(relay_host)


### MAIN:

if __name__ == "__main__":
    import optparse
    parser = optparse.OptionParser(
        usage= """
            Nagios SMTP smarthost check
            """,
        version=__version__)
    parser.add_option("-l", "--log-level",
        help="Adjust the logging level. Suitable values include "
        "10 (DEBUG), 20 (INFO), 30 (WARNING), 40 (ERROR), 50 (CRITICAL). "
        "Default=%d" % LOG_LEVEL)
    parser.add_option("-r", "--relayhost",
        help="relay server/smarthost to check\n")
    parser.add_option("-u", "--username",
        help="username to use \n")
    parser.add_option("-p", "--password",
        help="password to use \n")
    parser.add_option("-a", "--alternate_port",
        help="alternative port number (25 default) \n")
    parser.add_option("-t," "--test_message",
        help="a directory pattern to include (string only - no regex)\n")
    parser.add_option("-s," "--secure",
        help="use TLS/SSL to test connectivity\n")

    parser.set_defaults(log_level=str(LOG_LEVEL))

    (options, args) = parser.parse_args()

    _logger.setLevel(int(options.log_level))

    if not options.relayhost:
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

