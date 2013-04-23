from __future__ import absolute_import, division, print_function, unicode_literals
import abc
import binascii

class Device(object):
    """Represents an automation device that has been bound to a
       DeviceProfile."""
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, locator, profile):
        self.locator = locator
        self.profile = profile
    
    def control(self, attribute, value):
        """Perform a control operation on this Device, waiting for the result.
           This is equivalent to calling get() on the return value from
           control_async."""
        return self.control_async(attribute, value).get()
    
    @abc.abstractmethod
    def control_async(self, attribute, value):
        """Request that an attribute of this Device be set to a new value. A
           gevent.event.AsyncResult will be returned to permit waiting for
           the operation's completion."""
        pass
    
    def interrogate(self, attribute):
        """Perform an interrogate operation on this Device, waiting for the
           result. This is equivalent to calling get() on the return value
           from control_async."""
        return self.interrogate_async(attribute).get()
    
    @abc.abstractmethod
    def interrogate_async(self, attribute):
        """Request that an attribute of this Device be retrieved. A
           gevent.event.AsyncResult will be returned to permit waiting for
           the operation's completion and obtaining the result."""
        pass

class DeviceProfile(object):
    """Represents a class of Device that can be communicated with."""
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractproperty
    def attributes(self):
        """Return a list of Attributes supported by this DeviceProfile."""
        pass
    
    @abc.abstractmethod
    def bind(self, locator):
        """Link this DeviceProfile to the specified Locator, returning a
           Device to enable access to the automation device."""
        pass

    @abc.abstractproperty
    def identifier(self):
        """Return the identifier for this DeviceProfile."""
        pass

class Domain(object):
    """Represents a network of Devices that can be accessed by the system."""
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, identifier):
        assert isinstance(identifier, unicode)
        self.identifier = identifier
    
    @abc.abstractproperty
    def active(self):
        """Return whether or not this Domain is ready for access."""
        pass
    
    @abc.abstractproperty
    def profiles(self):
        """Return a list of DeviceProfiles supported by this Domain."""
        pass
        
    @abc.abstractmethod
    def start(self):
        """Establish a connection to the automation network represented by
           this Domain on a new greenthread."""
        pass

    @abc.abstractmethod
    def stop(self):
        """Terminate the connection to the automation network."""
        pass

class Locator(object):
    """Represents the network address of a Device."""
    def __init__(self, domain, address):
        assert isinstance(domain, Domain)
        assert isinstance(address, bytes)
        self.domain = domain
        self.address = address

    def __str__(self):
        return self.__unicode__().encode()

    def __unicode__(self):
        addrstr = binascii.hexlify(self.address)
        return "{0}:{1}".format(self.domain.identifier, addrstr)
