from .device import Device
from ..command.turn_on import TurnOn
from ..command.turn_off import TurnOff

class LampLinc(Device):

    commands = []
    commands.append(TurnOn())
    commands.append(TurnOff())

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
        