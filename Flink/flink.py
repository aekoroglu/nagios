#!/usr/bin/env python3

import json
import requests
import optparse
import sys

def get_info(server,port,jobname):
    try:
        if server is None and port is None and jobname:
            print ('Server IP address or hostname, TCP port and job name is required')
            sys.exit(2)
        else:
            flink_url = 'http://%s:%s/jobs/overview' %(server,port)
            r = requests.get(flink_url,timeout=3)
            res = r.json()
            jobs = res['jobs']
            job_list = []

            for i in jobs:
                if i['state'] == 'RUNNING':
                    job_list.append(i['name'])
            
            if jobname in job_list:
                print('OK : %s is running' % jobname)
                sys.exit(0)
            else:
                print('CRITICAL : %s is not running' % jobname)
                sys.exit(2)
    except Exception as e:
        print('CRITICAL : %s' % e)
        sys.exit(2)

def help_parser():
    parser = optparse.OptionParser(usage="usage: %prog -s 192.168.1.1 -P 7081 -j session-aggregator", version="%prog 1.0")
    parser.add_option('-s', '--server', action='store', type='string', dest='server', default=None, help='IP address or hostname you want to connect')
    parser.add_option('-P', '--port', action='store', type='int', dest='port', default=None, help="TCP port")
    parser.add_option('-j', '--jobname', action='store', type='string', dest='jobname', default=None, help='Flink job name')
    return parser

def main():
    parser = help_parser()
    options, _args = parser.parse_args()
    get_info(options.server,options.port,options.jobname)

if __name__ == "__main__":
    main()
