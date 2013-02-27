import sys
import os.path
#hack to add top directory to import searching path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import bridgehub
from services.io.insteon_service import InsteonIMService

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
    config = configuration()

    hub = bridgehub.BridgeHub(config)
    hub.run()

    	
if __name__ == '__main__':
    main()
