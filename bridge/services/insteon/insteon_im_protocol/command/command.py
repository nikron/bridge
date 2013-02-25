from abc import ABCMeta, abstractmethod

class Command():
    __metaclass__ = ABCMeta

    @abstractmethod
    def encode(self):
        pass
        
    @abstractmethod
    def getCommandBytes(self):
        pass
