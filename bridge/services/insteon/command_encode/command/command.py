from abc import ABCMeta, abstractmethod

class Command(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def getStructure(self):
        '''test'''
        
    @abstractmethod
    def getCommandBytes(self):
        '''test'''
                