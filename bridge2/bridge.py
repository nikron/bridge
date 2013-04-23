#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
import argparse
import gevent.pool
import grp
import os
import pwd
import sys

class Bridge(object):
    N_CONCURRENT_CACHE_FILLS = 5
    
    def __init__(self, config):
        self._config = config
    
    def init(self):
        for domain in self._config.domains:
            domain.start()
        # TODO: Fire up the Web listener
    
    def _popcache(self):
        # Run a query on every cacheable attribute to fill the cache
        pool = gevent.pool.Pool(cls.N_CONCURRENT_CACHE_FILLS)
        for asset in self._config.assets:
            for attr in asset.attributes:
                if attr.cacheable and not attr.config:
                    pool.spawn(asset.query, asset, attr)

    def run(self):
        self._popcache()
        # TODO: Stall indefinitely

def find_creds(uname):
    entry = pwd.getpwnam(uname)
    uid = entry.pw_uid
    gid = entry.pw_gid
    sgroups = []
    for group in grp.getgrall():
        if uname in group.gr_mem:
            sgroups.append(group.gr_gid)
    return uid, gid, sgroups

def go():
    try:
        args = parse_args()
        if args.uname != None:
            creds = find_creds(self._uname)
        # TODO: Load configuration
        bridge = Bridge(cds)
        bridge.init()
        if args.uname != None:
            switch_creds(*creds)
        bridge.run()
        return 0
    except Exception as e:
        print(b"Error: {0}".format(e), file=sys.stderr)
        return 1

def parse_args():
    desc = "Provide access to a home automation system over the network."
    ap = argparse.ArgumentParser(description=desc)
    ap.add_argument("-p",
                    type=int,
                    required=True,
                    help="port to listen on",
                    dest="port")
    ap.add_argument("-u",
                    type=unicode,
                    help="user account to run as",
                    dest="uname")
    ap.add_argument("-c",
                    type=unicode,
                    help="configuration file",
                    dest="config")
    args = ap.parse_args()
    if args.port < 1 or args.port > 65535:
        raise ValueError("argument -p: value out of range")
    return args

def switch_creds(uid, gid, sgroups):
    os.setresgid(gid, gid, gid)
    os.setgroups(sgroups)
    os.setresuid(uid, uid, uid)

if __name__ == "__main__":
    sys.exit(go())
