#!/usr/bin/python3

import os.path

import argparse

from bridge.hub import BridgeHub
from bridge.config import BridgeConfiguration

def parse_opts(default):
    parser = argparse.ArgumentParser(description='Control your devices!')
    parser.add_argument('-c', '--configuration', help='File to read configuration from', default=default)
    parser.add_argument('-d', '--directory', help='Directory to store data') 

    args = parser.parse_args()
    config = BridgeConfiguration(args.configuration)

    return config

def main():
    #TODO: reading in options
    #TODO: reading in configuration
    this_dir = os.path.dirname(__file__)
    default_config_file = os.path.join(os.path.abspath(this_dir), 'bridge.ini')

    config = parse_opts(default_config_file)

    hub = BridgeHub(config)
    hub.run()


if __name__ == '__main__':
    main()
