#!/usr/bin/python

"""
tell the world we are host X, at IP Y
The world is shell.devel.redhat.com, at port 15655
"""
from defines import *
PORT = IN_SERVER_PORT
HOST = REMOTES_SERVER_HOST

import socket
import time
import os
import re

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            s.connect((HOST, PORT))
            s.send('%s,%s\n' % (gethostname(), getip()))
            s.close()
        except Exception, e:
            print "Exception: %s" % e
        time.sleep(60)

def gethostname():
    with os.popen('hostname') as f:
        ret = f.read().strip()
    return ret

def getip():
    options = [(x.split()[1], x.split()[3].split('/')[0]) for x in [x for x in os.popen('ip -o addr show').readlines() if re.match('(^[a-z]+)', x.split()[1]).groups()[0] not in ['lo', 'tap', 'virbr'] if x.split()[2] == 'inet']]
    return options[0][1]

if __name__ == '__main__':
    main()
