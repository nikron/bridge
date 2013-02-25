from abc import ABCMeta, abstractmethod

from ..command.command import TurnOn, TurnOff
from ..insteon_exception import InsteonException

class Device(metaclass = ABCMeta):
        #byteToCommand = {"1200" : TurnOn, "1400" : TurnOff}
            
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

#This can't really be handled here, no way to know what device a command is for
#before decoding it        
#        def decodeCommand(self, response):
#            #strip "0x" format from beginning of response string, if necessary
#            if (response[0:2] == "0x"):
#                response = response[2:20]
#            
#            #should this always be 02?
#            if (response[0:2] != "02"):
#                raise InsteonException("Invalid Device Category!")
#                
#            #should this always be 62?
#            if (response[2:4] != "62"):
#                raise InsteonException("Invalid Command Number!")
#                
#            #this should always work!
#            deviceId = response[4:10]
#                    
#            #can be changed to accommodate extended messages later
#            if (bin(int(response[10:12], 16))[-1] == 1): # extended message
#                raise InsteonException("Do not use extended message yet!")
#       
#            #this could be done much more elegantly
#            if (response[12:14] != "12" and response[12:14] != "14"):
#                raise InsteonException("Command not recognized!")
#            
#            #this should always work too!
#            command = self.byteToCommand.get(response[12:16])
#       
#            #pack up ack/nak and deviceId into a dictionary
#            return {"ack" : (True if response[16:18] == "06" else False), "device" : deviceId,
#                    "command" : command}
#                    
