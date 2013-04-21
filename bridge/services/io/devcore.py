import abc
import binascii

class DeviceProfile(metaclass=abc.ABCMeta):
    @abc.abstractproperty
    def attributes(self):
        pass
    
    @abc.abstractmethod
    def control(self, locator, attribute, value)
        pass
        
    @abc.abstractmethod
    def find_attribute(self, identifier):
        pass
        
    @abc.abstractproperty
    def identifier(self):
        pass
    
    @abc.abstractmethod
    def interrogate(self, locator, attribute)
        pass

class Domain(metaclass=abc.ABCMeta)
    def __init__(self, identifier):
        self.identifier = identifier
        
    @abc.abstractmethod
    def find_profile(self, identifier):
        pass
        
    @abc.abstractmethod
    def monitor(self):
        pass
        
    @abc.abstractproperty
    def profiles(self):
        pass

class Locator():
    def __init__(self, domain, address):
        self.domain = domain
        self.address = address

    def __str__(self):
        return "{0}:{1}".format(self.domain, binascii.hexlify(self.address))
