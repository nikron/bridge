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
