import abc
import gevent
import gevent.event
import gevent.select
import serial
from bridge.services.io.devcore import Domain, Locator
from bridge.services.io.profiles import *
from insteon_protocol import insteon_im_protocol

class _InsteonDevice(Device):
    def __init__(self, locator, profile):
        super().__init__(locator, profile)
    
    def control_async(self, attribute, value):
        # Validate arguments
        assert attribute != None
        assert value != None
        if not attribute in self.profile.attributes:
            raise ValueError("Only attributes of this device are permitted")
        if not attribute.space.validate(value):
            raise ValueError("Illegal attribute value")
            
        # Delegate to the profile
        res = AsyncResult()
        fn = self.profile._control
        gevent.spawn(fn, self.locator, attribute, value).link(res)
        return res
    
    def interrogate_async(self, attribute):
        # Validate arguments
        assert attribute != None
        if not attribute in self.profile.attributes:
            raise ValueError("Only attributes of this device are permitted")
        if not attribute.space.validate(value):
            raise ValueError("Illegal attribute value")
            
        # Delegate to the profile
        res = AsyncResult()
        fn = self.profile._interrogate
        gevent.spawn(fn, self.locator, attribute).link(res)
        return res

class InsteonDeviceProfile(DeviceProfile, metaclass=abc.ABCMeta):
    def bind(self, locator):
        # Validate arguments
        if locator == None or not isinstance(locator, Locator):
            raise ValueError("The specified value is not a locator")
        if not isinstance(locator.domain, InsteonDomain):
            raise ValueError("This profile supports only Insteon devices")
        if not isinstance(locator.address, bytes) or len(locator.address) != 3:
            raise ValueError("The specified locator address is not valid")
            
        # Delegate to the InsteonDomain
        return locator.domain._bind(locator, self)
    
    @abc.abstractmethod
    def _control(self, locator, attribute, value):
        pass
        
    @abc.abstractmethod
    def _interrogate(self, locator, attribute):
        pass

class InsteonDomain(Domain):
    _plist = [
        PowerDeviceProfile(),
        DimmablePowerDeviceProfile()
    ]
    _pmap = {p.identifier: p for p in _plist}
    
    def __init__(self, identifier, modem_device):
        super().__init__(identifier)
        self._bindings = {}
        self._serdev = serial.Serial(modem_device, 19200)
    
    def _bind(self, locator, profile):
        # Store the binding, unless one already exists
        if address in self._bindings:
            raise ValueError("The specified address is already bound")
        self._bindings[address] = profile
        
        # Produce an InsteonDevice for the caller
        return _InsteonDevice(locator, profile)
    
    def monitor(self):
        while True:
            gevent.select.select([self._serdev.fileno()], None, None)
            buf = insteon_im_protocol.read_command(self._serdev)
            if buf != None:
                update = insteon_im_protocol.decode(buf)
                # FIXME: Do something here
    
    @property
    def profiles(self):
        return self._plist

    def _xmit(self, address, cmd):
        raise NotImplementedError()
