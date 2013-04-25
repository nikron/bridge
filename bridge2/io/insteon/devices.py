from __future__ import absolute_import, division, print_function, unicode_literals
import abc
import gevent
from bridge2.io.devices import *
from bridge2.io.insteon.modem.client import *
from bridge2.io.insteon.profiles import *
from bridge2.model.attributes import *

class _InsteonDevice(Device):
    def __init__(self, locator, profile):
        super(_InsteonDevice, self).__init__(locator, profile)
    
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
    
    def subscribe(self, attribute, fn):
        pass

class InsteonDomain(Domain):
    """Represents a network of Devices that can be accessed by the system."""
    _plist = [
        PowerDeviceProfile(),
        DimmablePowerDeviceProfile()
    ]
    _pmap = {p.identifier: p for p in _plist}
    
    def __init__(self, identifier, port):
        super(InsteonDomain, self).__init__(identifier)
        self._client = InsteonClient(port)
        self._client.subscribe(self._handlemsg)
        self._bindings = {}
    
    def active(self):
        return self._client.active
    
    def _bind(self, locator, profile):
        # Store the binding, unless one already exists
        if address in self._bindings:
            raise ValueError("The specified address is already bound")
        self._bindings[address] = profile
        
        # Produce an InsteonDevice for the caller
        return _InsteonDevice(locator, profile)
    
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
        return InsteonDomain._plist
    
    def start(self):
        self._client.start()

    def stop(self):
        self._client.stop()
