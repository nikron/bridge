from __future__ import absolute_import, division, print_function, unicode_literals
from bridge2.io.devices import *
from bridge2.io.insteon.devices import *
from bridge2.io.insteon.modem.client import *
from bridge2.model.attributes import *

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
        return InsteonDeviceRef(locator, profile)
    
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
