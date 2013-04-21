import gevent.select
import serial
from bridge.services.io.devcore import Domain
from bridge.services.io.profiles import *
from insteon_protocol import insteon_im_protocol

class InsteonDomain(Domain):
    _pmap = map(Domain.identifier, [
        PowerDeviceProfile(),
        DimmablePowerDeviceProfile()
    ])
    _plist = _pmap.viewvalues()
    
    def __init__(self, modem_device):
        self._serdev = serial.Serial(modem_device, 19200)
    
    def find_profile(self, identifier):
        return self._pmap.get(identifier)
    
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
