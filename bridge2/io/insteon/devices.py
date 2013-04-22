from __future__ import absolute_import, division, print_function, unicode_literals
import abc
import gevent
import gevent.event
import serial
from bridge2.io.devices import Device, DeviceProfile, Domain, Locator
from bridge2.io.insteon.modem import ModemPDU
from bridge2.io.insteon.profiles import *
from bridge2.model.attributes import Attribute
from insteon_protocol import insteon_im_protocol

class _InsteonDevice(Device):
    def __init__(self, locator, profile):
        super(_InsteonDevice, self).__init__(locator, profile)
    
    def control_async(self, attribute, value):
        # Validate arguments
        assert isinstance(attribute, Attribute)
        assert value != None
        if not attribute in self.profile.attributes:
            raise ValueError("Only attributes of this device are permitted")
        if not attribute.space.validate(value):
            raise ValueError("Illegal attribute value")
            
        # Delegate to the profile
        res = gevent.event.AsyncResult()
        fn = self.profile._control
        gevent.spawn(fn, self.locator, attribute, value).link(res)
        return res
    
    def interrogate_async(self, attribute):
        # Validate arguments
        assert isinstance(attribute, Attribute)
        if not attribute in self.profile.attributes:
            raise ValueError("Only attributes of this device are permitted")
            
        # Delegate to the profile
        res = gevent.event.AsyncResult()
        fn = self.profile._interrogate
        gevent.spawn(fn, self.locator, attribute).link(res)
        return res

class InsteonDomain(Domain):
    _plist = [
        PowerDeviceProfile(),
        DimmablePowerDeviceProfile()
    ]
    _pmap = {p.identifier: p for p in _plist}
    
    def __init__(self, identifier, devfile):
        super(InsteonDomain, self).__init__(identifier)
        self._bindings = {}
        self._serdev = serial.Serial(devfile, 19200, timeout=0, writeTimeout=0)
    
    def _bind(self, locator, profile):
        # Validate arguments
        assert isinstance(locator, Locator)
        if not isinstance(locator.domain, InsteonDomain):
            raise ValueError("This profile supports only Insteon devices")
        if not isinstance(locator.address, bytes) or len(locator.address) != 3:
            raise ValueError("The specified address is not valid")

        # Store the binding, unless one already exists
        if address in self._bindings:
            raise ValueError("The specified address is already bound")
        self._bindings[address] = profile
        
        # Produce an _InsteonDevice for the caller
        return _InsteonDevice(locator, profile)
    
    def monitor(self):
        while True:
            pdu = ModemPDU.readfrom(self._serdev, self._read_nblock)
            # FIXME: Do something here
            if isinstance(pdu, StdMessageModemPDU):
                pass
            if isinstance(pdu, ExtMessageModemPDU):
                pass
    
    @staticmethod
    def _read_nblock(f, n):
        data = ""
        nread = 0
        while nread < n:
            gevent.select.select([f], [], [])
            data2 = f.read(n)
            nread += len(data2)
            data += data2
        return data
    
    @property
    def profiles(self):
        return self._plist

    def _xmit(self, address, cmd):
        raise NotImplementedError()
