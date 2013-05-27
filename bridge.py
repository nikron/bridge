#!/usr/bin/python3
import os, sys

import argparse
import logging

from bridge.hub import BridgeHub
from bridge.config import BridgeConfiguration

def parse_opts(default):
    """
    Parse options, default is default configuration file.
    """
    parser = argparse.ArgumentParser(description="Control your devices!")
    parser.add_argument("-s", "--stderr", help="Output log to stderr.", action="store_true")
    parser.add_argument("-c", "--configuration", help="File to read configuration from.", default=default)
    parser.add_argument("-d", "--daemonize", help="Fork to the background.", action='store_true')

    opts = parser.parse_args()

    return opts

def daemonize(stdin=os.devnull, stdout=os.devnull, stderr=os.devnull):
    pid = os.fork()
    if pid > 0:
        sys.exit(0)

    # decouple from parent environment
    os.chdir("/")
    os.setsid()
    os.umask(0)

    pid = os.fork()
    if pid > 0:
        sys.exit(0)

def main():
    """
    Get configuratin of hub by parsing options, then passsing them
    to bridge config.
    """
    this_dir = os.path.dirname(__file__)
    default_config_file = os.path.join(os.path.abspath(this_dir), 'bridge.ini')

    opts = parse_opts(default_config_file)
    config = BridgeConfiguration(opts.configuration, opts.stderr)

    hub = BridgeHub(config)
    if opts.daemonize:
        daemonize()
    hub.run()

if __name__ == '__main__':
    main()
