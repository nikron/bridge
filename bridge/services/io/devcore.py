import abc
import binascii

class Device(metaclass=abc.ABCMeta):
    def __init__(self, locator, profile):
        self.locator = locator
        self.profile = profile
    
    def control(self, attribute, value):
        return self.control_async(attribute, value).get()
    
    @abc.abstractmethod
    def control_async(self, attribute, value):
        pass
    
    def interrogate(self, attribute):
        return self.interrogate_async(attribute).get()
    
    @abc.abstractmethod
    def interrogate_async(self, attribute):
        pass

class DeviceProfile(metaclass=abc.ABCMeta):
    @abc.abstractproperty
    def attributes(self):
        pass
    
    @abc.abstractmethod
    def bind(self, locator):
        pass

    @abc.abstractproperty
    def identifier(self):
        pass

class Domain(metaclass=abc.ABCMeta):
    def __init__(self, identifier):
        self.identifier = identifier
    
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
        addrstr = binascii.hexlify(self.address)
        return "{0}:{1}".format(self.domain.identifier, addrstr)
