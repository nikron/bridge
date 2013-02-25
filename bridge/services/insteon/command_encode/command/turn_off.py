from .command import Command

class TurnOff(Command):    
    def __init__(self, deviceId):
        super().__init__()
        self.command = b"0262" + deviceId + b"001400"
        
    def encode(self):
        return self.command
    
    def getCommandBytes(self):
        return "1400"
