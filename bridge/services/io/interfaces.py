import serial


def create_interface(config):
    interfaces = { 
                'serial' : serial.Serial, 
             }

    name = config[0]
    if name is 'none':
        return None

    target = config[1]
    args = config[2]

    return interfaces[name](target, *args)
