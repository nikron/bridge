from __future__ import absolute_import, division, print_function, unicode_literals
import abc
import binascii

class Device(object):
    """Represents an automation device that has been bound to a
       DeviceProfile."""
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, locator, profile):
        assert isinstance(locator, Locator)
        assert isinstance(profile, DeviceProfile)
        self._locator = locator
        self._profile = profile
    
    @abc.abstractmethod
    def control(self, attribute, value):
        """Commit a new value to an Attribute of this Device."""
        pass
    
    @abc.abstractmethod
    def interrogate(self, attribute):
        """Query this Device for the value of an Attribute."""
        pass
        
    @property
    def locator(self):
        """Return the Locator for this Device."""
        return self._locator
    
    @property
    def profile(self):
        """Return the DeviceProfile associated with this Device."""
        return self._profile

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
        self._identifier = identifier
    
    @abc.abstractproperty
    def active(self):
        """Return whether or not this Domain is ready for access."""
        pass
    
    @abc.abstractmethod
    def check_address(self, address):
        """Determine whether or not the specified address is valid within
           this Domain."""
        pass
    
    @property
    def identifier(self):
        """Return the identifier for this Domain."""
        return self._identifier
    
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
        if not domain.check_address(address):
            raise ValueError("The specified address is not acceptable")
        self._domain = domain
        self._address = address

    @property
    def address(self):
        """Return the address described by this Locator."""
        return self._address

    @property
    def domain(self):
        """Return the Domain the address corresponds to."""
        return self._domain

    def __str__(self):
        return self.__unicode__().encode()

    def __unicode__(self):
        addrstr = binascii.hexlify(self._address)
        return "{0}:{1}".format(self._domain.identifier, addrstr)
