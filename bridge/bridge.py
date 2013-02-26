import sys
import os.path
#hack to add top directory to import searching path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import bridgehub


def configuration():
    return {}

def main():
    #TODO: reading in options
    #TODO: reading in configuration
    config = configuration()

    hub = bridgehub.BridgeHub(config)
    hub.run()

    	
if __name__ == '__main__':
    main()
