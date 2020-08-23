#!/usr/bin/env python3

import json
import requests
import optparse
import sys

def get_info(server,port):
    try:
        if server is None and port is None:
            print ('Server IP address or hostname and TCP port is required')
            sys.exit(2)
        else:
            solr_url = 'http://%s:%s/solr/admin/collections?action=CLUSTERSTATUS&wt=json' %(server,port)
            r = requests.get(solr_url,timeout=3)
            res = r.json()
            node_name = '%s:%s_solr' % (server,port)
            cluster = res['cluster'].get("live_nodes")
            if node_name in cluster:
                print('OK: Solr node is live')
                sys.exit(0)
            else:
                print('CRITICAL : Solr node is dead')
                sys.exit(2)
    except Exception as e:
        print('CRITICAL : %s' % e)
        sys.exit(2)

def help_parser():
    parser = optparse.OptionParser(usage="usage: %prog -s 192.168.1.1 -P 8983", version="%prog 1.0")
    parser.add_option('-s', '--server', action='store', type='string', dest='server', default=None, help='IP address or hostname you want to connect')
    parser.add_option('-P', '--port', action='store', type='int', dest='port', default=None, help="TCP port")
    return parser

def main():
    parser = help_parser()
    options, _args = parser.parse_args()
    get_info(options.server,options.port)

if __name__ == "__main__":
    main()
