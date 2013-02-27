import sys
import os.path
current_dir = os.path.dirname(__file__)
#hack to add top directory to import searching path
sys.path.append(os.path.abspath(os.path.join(current_dir, os.path.pardir)))

import argparse

import bridgehub
from bridgeconfig import BridgeConfiguration
from services.io.insteon_service import InsteonIMService

def parse_opts(default):
    parser = argparse.ArgumentParser(description='Control your devices!')
    parser.add_argument('-c', '--configuration', help='File to read configuration from', default=default)
    parser.add_argument('-d', '--directory', help='Directory to store data') 

    args = parser.parse_args()
    config = BridgeConfiguration(args.configuration)

    return config

#have to dynamcially read this from a file and rutime options in future
def configuration():
    return { 'Model Driver' : 'file',
            'IO Services' : [{ 
                'driver' : InsteonIMService,
                'name' : 'insteon io service',
                'interface' : ('none', '/dev/ttyUSB0', [])}],
            }

def main():
    #TODO: reading in options
    #TODO: reading in configuration
    default_config_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'bridge.config')

    config = parse_opts(default_config_file)

    config = configuration()

    hub = bridgehub.BridgeHub(config)
    hub.run()

    	
if __name__ == '__main__':
    main()
