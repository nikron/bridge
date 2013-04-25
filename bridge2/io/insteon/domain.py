from __future__ import absolute_import, division, print_function, unicode_literals
import abc
import gevent
from bridge2.io.devices import *
from bridge2.io.insteon.modem.client import *
from bridge2.model.attributes import *

class _InsteonDeviceRef(DeviceRef):
    def __init__(self, locator, profile):
        super(_InsteonDeviceRef, self).__init__(locator, profile)
    
    def control(self, attribute, value):
        # Validate arguments
        assert isinstance(attribute, Attribute)
        if not attribute in self.profile.attributes:
            raise ValueError(b"Only attributes of this device are permitted")
        if not attribute.writable:
            raise ValueError(b"The specified attribute is not writable")
        if not attribute.space.validate(value):
            raise ValueError(b"Illegal attribute value")
            
        # Delegate to the profile
        addr = self.locator.address
        return self.profile._control(addr, attribute, value)
    
    def interrogate(self, attribute):
        # Validate arguments
        assert isinstance(attribute, Attribute)
        if not attribute in self.profile.attributes:
            raise ValueError(b"Only attributes of this device are permitted")
        if not attribute.readable:
            raise ValueError(b"The specified attribute is not readable")
            
        # Delegate to the profile
        addr = self.locator.address
        return self.profile._interrogate(addr, attribute)
    
    def subscribe(self, fn):
        pass

class InsteonDeviceProfile(DeviceProfile):
    def bind(self, locator):
        assert isinstance(locator, Locator)
        return locator.domain._bind(locator, self)
    
    @abc.abstractmethod
    def _control(self, address, attribute, value):
        pass
        
    @abc.abstractmethod
    def _dispatch(self, src, dest, msg):
        pass
        
    @abc.abstractmethod
    def _interrogate(self, address, attribute):
        pass

class InsteonDomain(Domain):
    """Represents a network of Devices that can be accessed by the system."""
    def __init__(self, identifier, port):
        super(InsteonDomain, self).__init__(identifier)
        self._client = InsteonClient(port)
        self._client.subscribe(self._handlemsg)
        self._bindings = {}
    
    def active(self):
        return self._client.active
    
    def _bind(self, locator, profile):
        # Store the binding, unless one already exists
        assert profile in self._profiles
        if address in self._bindings:
            raise ValueError(b"The specified address is already bound")
        self._bindings[address] = profile
        
        # Produce an _InsteonDeviceRef for the caller
        return _InsteonDeviceRef(locator, profile)
    
    def check_address(self, address):
        if not isinstance(address, bytes):
            return False
        if len(address) != 3:
            return False
        return True
    
    def _handlemsg(self, src, dest, msg):
        dev = self._bindings.get(src)
        if dev == None:
            return
        srcl = Locator(self, src)
        destl = Locator(self, dest)
        dev.profile._dispatch(srcl, destl, msg)
    
    def _notify(self, target, event):
        raise NotImplementedError()
    
    @property
    def port(self):
        return self._client.port
    
    @property
    def profiles(self):
        return self._profiles
    
    def start(self):
        self._client.start()

    def stop(self):
        self._client.stop()

from bridge2.io.insteon.profiles import *
InsteonDomain._profiles = [
    PowerDeviceProfile(),
    DimmablePowerDeviceProfile()
]
