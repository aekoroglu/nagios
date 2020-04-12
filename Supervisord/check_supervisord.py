#!/usr/bin/env python3

#
# Supervisord plugin for Nagios by Ali Erdinc Koroglu
# 
# Licensed under the GNU General Public License v3.0
# See the file https://www.gnu.org/licenses/gpl-3.0.txt
#

from xmlrpc.client import ServerProxy
import optparse
import sys

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
        return 'UNKNOWN'


def get_state(process, state, desc, now, start, warning, critical, time):
    tdiff = now - start
    if time == 'minute':
        proc_upt = round(tdiff/60,2)
    elif time == 'hour':
        proc_upt = round(tdiff/3600,2)
    elif time == 'day':
        proc_upt = round(tdiff/86400,2)
    else:
        proc_upt = tdiff

    if warning is None and critical is None:
        print ('%s %s: %s | uptime=%s;;;' % (process, state, desc, proc_upt))
        sys.exit(0)
    elif critical is None:
        if proc_upt <= warning:
            print('%s WARNING : %s | uptime=%s;%s;;' % (process, desc, proc_upt, warning))
            sys.exit(1)
        else:
            print ('%s %s: %s | uptime=%s;%s;;' % (process, state, desc, proc_upt, warning))
            sys.exit(0)
    elif warning is None:
        if proc_upt < critical:
            print('%s CRITICAL : %s | uptime=%s;;%s;' % (process, desc, proc_upt, critical))
            sys.exit(2)
        else:
            print ('%s %s: %s | uptime=%s;;%s;' % (process, state, desc, proc_upt, critical))
            sys.exit(0)
    else:
        if warning <= critical:
            print ('CRITICAL : Warning value can not be less than or equal to critical')
            sys.exit(2)
        else:
            if proc_upt < critical:
                print('%s CRITICAL : %s | uptime=%s;%s;%s;' % (process, desc, proc_upt, warning, critical))
                sys.exit(2)
            elif proc_upt <= warning:
                print('%s WARNING : %s | uptime=%s;%s;%s;' % (process, desc, proc_upt, warning, critical))
                sys.exit(1)
            else:
                print ('%s %s: %s | uptime=%s;%s;%s;' % (process, state, desc, proc_upt, warning, critical))
                sys.exit(0)


def get_info(server,port,username,password,process,warning,critical,time):
    try:
        if server is None and port is None:
            print ('Server and port is required')
            sys.exit(2)
        elif process is None:
            print ('Process is required')
            sys.exit(2)
        
        if username is None and password is None:
            uri = 'http://%s:%s/RPC2' % (server,port)
        else:
            uri = 'http://%s:%s@%s:%s/RPC2' % (username,password,server,port)
        
        server = ServerProxy(uri)
        proc_info = server.supervisor.getProcessInfo(process)
        proc_state = superv_state(proc_info['statename'])
        proc_desc = proc_info['description']
        proc_now = proc_info['now']
        proc_start = proc_info['start']
        get_state(process, proc_state, proc_desc, proc_now, proc_start, warning, critical, time)
    except Exception as e:
        print('CRITICAL : %s' % e)
        sys.exit(2)


def help_parser():
    parser = optparse.OptionParser(usage="usage: %prog -s 192.168.1.1 -P 9001 -u superv -p superv -a tomcat", version="%prog 2.0")
    parser.add_option('-s', '--server', action='store', type='string', dest='server', default=None, help='IP address or hostname you want to connect')
    parser.add_option('-P', '--port', action='store', type='int', dest='port', default=None, help="TCP port")
    parser.add_option('-u', '--username', action='store', type='string', dest='username', default=None, help="Username")
    parser.add_option('-p', '--password', action='store', type='string', dest='password', default=None, help="Password")
    parser.add_option('-a', '--process-name', action='store', type='string', dest='process', default=None, help="Process name")
    parser.add_option('-t', '--time', action='store', type='string', dest='time', default='minute', help="Time unit of measurement (second|minute|hour|day) (default: minutes)")
    parser.add_option('-w', '--warning', action='store', type='int', dest='warning', default=None, help='The warning threshold')
    parser.add_option('-c', '--critical', action='store', type='int', dest='critical', default=None, help='The critical threshold')
    return parser


def main():
    parser = help_parser()
    options, _args = parser.parse_args()
    get_info(options.server,options.port,options.username,options.password,options.process,options.warning,options.critical,options.time)


if __name__ == "__main__":
    main()
