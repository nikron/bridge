from __future__ import absolute_import, division, print_function, unicode_literals
from bridge2.io.attributes import *
from bridge2.io.devices import *
from bridge2.io.insteon.devices import *
from bridge2.io.insteon.modem import *

class PowerDeviceProfile(InsteonDeviceProfile):
    _attr_power = Attribute("power", BooleanSpace())
    _attributes = [_attr_power]
    
    @property
    def attributes(self):
        return self._attributes
    
    def _control(self, locator, attribute, value):
        if attribute == _attr_power:
            if value:
                cmd = InsteonMessage(InsteonMessage.DIRECT_CMD, 0x12, 0xFF)
            else:
                cmd = InsteonMessage(InsteonMessage.DIRECT_CMD, 0x14, 0)
            locator.domain._sendmsg(locator.address, cmd)
        else:
            raise ValueError(b"Unexpected attribute received")
    
    def _dispatch(self, src, dest, msg):
        print("[{0} -> {1}] {2}".format(src, dest, msg))
    
    @property
    def identifier(self):
        return "power"
    
    def _interrogate(self, locator, attribute):
        if attribute == _attr_power:
            raise NotImplementedError()
        else:
            raise ValueError(b"Unexpected attribute received")
