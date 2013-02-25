from .command import Command

class TurnOn(Command):
    def __init__(self, deviceId):
        super().__init__()
        self.command = b"0262" + deviceId + b"001200"

    def encode(self):
        return self.command
    
    def getCommandBytes(self):
        return "1200"
