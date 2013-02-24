from .command import Command

class TurnOn(Command):
    def __init__(self):
        Command.__init__(self)
        
    def getStructure(self):
        return "0x0262{deviceId}001200"
    
    def getCommandBytes(self):
        return "1200"
