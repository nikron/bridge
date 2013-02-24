from .command import Command

class TurnOff(Command):    
    def __init__(self):
        Command.__init__(self)
        
    def getStructure(self):
        return "0x0262*001400"
    
    def getCommandBytes(self):
        return "1400"