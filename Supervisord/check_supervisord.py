#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Supervisord plugin for Nagios by Ali Erdinc Koroglu - http://ae.koroglu.org
# Licensed under the GNU General Public License, version 2.
# See the file http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt

import xmlrpclib
import socket
from socket import error as socket_error
import datetime
from dateutil.relativedelta import relativedelta
from optparse import OptionParser
import sys

usage = "usage: %prog -H 192.168.1.1 -P 9001 -u superv -p superv -a glassfish"
parser = OptionParser(usage=usage)
parser.add_option('-H', '--hostname', dest='hostname', help="Supervisord hostname")
parser.add_option('-P', '--port', dest='port', help="Supervisord port")
parser.add_option('-u', '--username', dest='username', help="Supervisord username")
parser.add_option('-p', '--password', dest='password', help="Supervisord password")
parser.add_option('-a', '--process-name', dest='procname', help="Process name defined in /etc/supervisor.d/*.ini or supervisorctl status")
(opts, args) = parser.parse_args()

def superv_state(state):
    if state == 'RUNNING':
        return 'OK'
    elif state == 'STOPPED':
        return 'WARNING'
    elif state == 'STOPPING':
        return 'WARNING'
    elif state == 'STARTING':
        return 'WARNING'
    elif state == 'EXITED':
        return 'CRITICAL'
    elif state == 'BACKOFF':
        return 'CRITICAL'
    elif state == 'FATAL':
        return 'CRITICAL'
    else:
        return 'UNKOWN'

def time_diff_text(diff):
    if diff.days >= 1:
        return '%s day(s) %s hour(s) %s minute(s)' % (diff.days, diff.hours, diff.minutes)
    elif diff.hours > 1:
        return '%s hour(s) %s minute(s)' % (diff.hours, diff.minutes)
    else:
        return '%s minute(s)' % (diff.minutes)

def proper_exit(status):
    if status == 'OK':
        sys.exit(0)
    elif status == 'WARNING':
        sys.exit(1)
    elif status == 'CRITICAL':
        sys.exit(2)
    else:
        sys.exit(3)

def superv_status(hostname,port,username,password,procname):
    try:
        if hostname is None or port is None:
            parser.print_help()
            sys.exit()
        if username is None and password is None:
            serverurl = "http://%s:%s" % (hostname,port)
        else:
            serverurl = "http://%s:%s@%s:%s" % (username,password,hostname,port)
        socket.setdefaulttimeout(10)
        server = xmlrpclib.Server(serverurl)
        info = server.supervisor.getProcessInfo(procname)
        sprv_status = superv_state(info['statename'])
        time1 = datetime.datetime.fromtimestamp(info['start'])
        time2 = datetime.datetime.fromtimestamp(info['now'])
        diff = relativedelta(time2,time1)
        uptime_text = time_diff_text(diff)
        print '%s %s: %s' % (procname, sprv_status, uptime_text)
        proper_exit(sprv_status)
    except (socket_error,xmlrpclib.ProtocolError,xmlrpclib.ResponseError), error_code:
        print "CRITICAL: Could not connect to supervisord %s" % error_code
        sys.exit(2)
    except Exception, error_code:
        print "CRITICAL: %s" % error_code
        sys.exit(2)

superv_status(opts.hostname,opts.port,opts.username,opts.password,opts.procname)
