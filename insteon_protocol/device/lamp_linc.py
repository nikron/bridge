from .device import Device
from ..command.commands import TurnOn, TurnOff
import logging

class LampLinc(Device):
    def __init__(self):
        super().__init__()

        '''initialize commands here'''
        self.commands = [TurnOn, TurnOff]
        #self.commands.append(TurnOn())
        #self.commands.append(TurnOff())

    def encodeCommand(self, command, deviceId):
        if command not in self.commands:
            logging.error("{0} is not a valid command for us".format(repr(command)))
        else:
            return super().encodeCommand(command, deviceId)
            
    def getCommands(self):
        return self.commands
        
