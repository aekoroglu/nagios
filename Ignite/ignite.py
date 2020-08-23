#!/usr/bin/env python3

import json
import requests
import optparse
import sys
import time

def get_info(server,port):
    try:
        if server is None and port is None:
            print ('Ignite IP address or hostname and TCP port is required')
            sys.exit(2)
        else:
            ignite_url = 'http://%s:%s/ignite?cmd=node&attr=true&mtr=true&ip=%s' %(server,port,server)
            r = requests.get(ignite_url,timeout=3)
            res = r.json()
            ignite_hostname = res["response"]["tcpHostNames"][0]
            ignite_upTime = res["response"]["metrics"]["upTime"]
            ignite_startTime = res["response"]["metrics"]["startTime"]
            ignite_cache = res["response"]["caches"][0]["name"]

            if "acc_" in ignite_cache:
                print('OK : %s (%s) is running' % (ignite_hostname,server))
                sys.exit(0)
            else:
                print('CRITICAL : %s (%s) is not running' % (ignite_hostname,server))
                sys.exit(2)
    except Exception as e:
        print('CRITICAL : %s' % e)
        sys.exit(2)

def help_parser():
    parser = optparse.OptionParser(usage="usage: %prog -s 192.168.1.1 -P 8080", version="%prog 1.0")
    parser.add_option('-s', '--server', action='store', type='string', dest='server', default=None, help='IP address or hostname you want to connect')
    parser.add_option('-P', '--port', action='store', type='int', dest='port', default=None, help="TCP port")
    return parser

def main():
    parser = help_parser()
    options, _args = parser.parse_args()
    get_info(options.server,options.port)

if __name__ == "__main__":
    main()
