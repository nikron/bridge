#!/usr/bin/python3
import os.path

import argparse

from bridge.hub import BridgeHub
from bridge.config import BridgeConfiguration

def parse_opts(default):
    """Parse options, default is default configuration file."""
    parser = argparse.ArgumentParser(description='Control your devices!')
    parser.add_argument('-s', '--stderr', help='Output log to stderr.', action='store_true')
    parser.add_argument('-c', '--configuration', help='File to read configuration from.', default=default)

    opts = parser.parse_args()

    return opts

def main():
    """
    Get configuratin of hub by parsing options, then passsing them
    to bridge config.
    """
    this_dir = os.path.dirname(__file__)
    default_config_file = os.path.join(os.path.abspath(this_dir), 'bridge.ini')

    opts = parse_opts(default_config_file)
    config = BridgeConfiguration(opts)

    hub = BridgeHub(config)
    hub.run()


if __name__ == '__main__':
    main()
