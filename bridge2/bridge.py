#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
import argparse
import gevent
import grp
import os
import pwd
import sys

def go():
    args = parse_args()
    if args.uname != None:
        switch_user(args.uname)
    try:
        for domain in config.domains:
            domain.start()
        for asset in config.assets:
            asset.load_cache()
        gevent.getcurrent().join()
    except KeyboardInterrupt:
        pass
    gevent.shutdown()

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

def switch_user(uname):
    entry = pwd.getpwnam(uname)
    uid = entry.pw_uid
    gid = entry.pw_gid
    sgroups = []
    for group in grp.getgrall():
        if uname in group.gr_mem:
            sgroups.append(group.gr_gid)
    os.setresgid(gid, gid, gid)
    os.setgroups(sgroups)
    os.setresuid(uid, uid, uid)

if __name__ == "__main__":
    try:
        go()
        sys.exit(0)
    except Exception as e:
        print(b"Error: {0}".format(e), file=sys.stderr)
        sys.exit(1)
