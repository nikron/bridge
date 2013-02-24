from .device import Device

class SwitchLinc(Device):

    commands = []

    def __init__(self):
        Device.__init__(self)
        '''initialize commands here'''

    def encodeCommand(self, deviceId, command):
        global commands
        
        if command not in commands:
            '''probably should throw an exception here'''
            pass 
        else:
            return super(Device, self).encodeCommandForDevice(deviceId, command, self)
            
    def getCommands(self):
        global commands
        return commands
        