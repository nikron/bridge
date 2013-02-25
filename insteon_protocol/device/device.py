from abc import ABCMeta, abstractmethod

from ..command.commands import TurnOn, TurnOff
from ..insteon_exception import InsteonException

class Device(metaclass = ABCMeta):
        @abstractmethod
        def getCommands(self):
            '''implement in all sub-classes'''
            
        #deviceType should be a class name, not sure if it will be used yet
        #why pass devicetype as a class name, it is what this method
        #should be called on
        def encodeCommand(self, command, deviceId):
            #return command.getStructure(self).format(deviceId=deviceId)

            #I figure it's much easier to send an individual command the id and it
            #handling how it should work out
            return command(deviceId).encode()
