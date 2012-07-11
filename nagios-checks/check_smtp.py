#!/usr/bin/python

import os, sys, datetime, stat
import smtplib, email.utils
import shutil, time, optparse, re
import logging

from email.mime.text import MIMEText

""" Script to check SMTP access

    :var LOG_LEVEL: This is the default logging level.  Here are suitable values:

    """
__author__ = "Andrew Stangl"
__date__ = "2012-07-11"
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

def check_queue()

    mailq_files = []
    queue_list = []

    if os.isfile('/usr/sbin/sendmail'):
        sendmail = True
        mailqdir = '/var/spool/mqueue/'
    else:
        _logger.error("MTA is not sendmail compatible, exiting...")
        raise SystemExit, UNKNOWN

    for root, dirs, files in os.walk(mailqdir):
        for filename in files:
            mailq_files.append(os.path.join(root, filename))
            queue_list.append(filename)

    if queue_list:
        _logger.debug("mailq is building up!!")
        print 'CRITICAL - MailQ %s has %s messages in it!! - %s' %(mailqdir, len(queue_list))
        raise SystemExit, CRITICAL
    else:
        _logger.debug("mailq is empty")
        print 'OK - MailQ %s is empty' %(mailqdir)
        raise SystemExit, OK


def run_check(relayhost='localhost', username, password, port='25', testmsg, secure='False', queue='False'):

    if queue:
        check_queue()

    ## establish connection
    try:
        server = smtplib.SMTP(relayhost, port)
        server.set_debuglevel('True')
        _logger.debug("Connection active: ")

        if username and password:
            try:
                server.login(username,password)
                print 'OK - connection to SMTP server %s available' %(relayhost)
                raise SystemExit, OK

            except SMTPAuthenticationError:
                print 'Cannot authenticate to specified SMTP server!!'
                raise SystemExit, CRITICAL
        else:
            print 'OK - connection to SMTP server %s available' %(relayhost)
            raise SystemExit, OK

    except SMTPConnectError:
        print 'Cannot connect to specified SMTP server!!'
        raise SystemExit, CRITICAL
        

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
    parser.add_option("-s," "--secure", action="store_true",
        help="use TLS/SSL to test connectivity\n")
    parser.add_option("-q," "--queue", action="store_true",
        help="Check if mailq building up - SENDMAIL specific\n")

    parser.set_defaults(log_level=str(LOG_LEVEL), relayhost='localhost',
        port='25', secure='False', queue='False')

    (options, args) = parser.parse_args()

    _logger.setLevel(int(options.log_level))

    if options.secure:
        queue = True
    else:
        queue = False

    if options.queue:
        queue = True
    else:
        queue = False

    run_check(relayhost, username, password, port, secure, queue)

