from abc import ABCMeta, abstractmethod

from ..command.turn_on import TurnOn
from ..command.turn_off import TurnOff
from ..insteon_exception import InsteonException

class Device(object):
        __metaclass__ = ABCMeta
        
        byteToCommand = {"1200" : TurnOn, "1400" : TurnOff}
            
        @abstractmethod
        def encodeCommand(self, deviceId, command):
            '''implement in all sub-classes'''
            
        @abstractmethod
        def getCommands(self):
            '''implement in all sub-classes'''
            
        #deviceType should be a class name, not sure if it will be used yet
        def encodeCommandForDevice(self, command, deviceId, deviceType):
            return command.getStructure(Device).replace("*", "" + deviceId)
        
        def decodeCommandFromDevice(self, response):
            global byteToCommand
            
            #strip "0x" format from beginning of response string, if necessary
            if (response[0:2] == "0x"):
                response = response[2:20]
            
            #should this always be 02?
            if (response[0:2] != "02"):
                raise InsteonException("Invalid Device Category!")
                
            #should this always be 62?
            if (response[2:4] != "62"):
                raise InsteonException("Invalid Command Number!")
                
            #this should always work!
            deviceId = response[4:10]
                    
            #can be changed to accommodate extended messages later
            if (bin(int(response[10:12], 16))[-1] == 1): # extended message
                raise InsteonException("Do not use extended message yet!")
       
            #this could be done much more elegantly
            if (response[12:14] != "12" and response[12:14] != "14"):
                raise InsteonException("Command not recognized!")
            
            #this should always work too!
            command = self.byteToCommand.get(response[12:16])
       
            #pack up ack/nak and deviceId into a dictionary
            return {"ack" : ("1" if response[16:18] == "06" else "0"), "device" : deviceId,
                    "command" : command}
                    
        
        
        
        
        
        
        
        
        