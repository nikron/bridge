from __future__ import absolute_import, division, print_function, unicode_literals
from bridge2.io.devices import *
from bridge2.io.insteon.devices import *
from bridge2.model.attributes import *

class DimmablePowerDeviceProfile(InsteonDeviceProfile):
    _attr_intensity = Attribute("intensity", IntegerSpace(0, 0xFF))
    _attributes = [_attr_intensity]
    
    @property
    def attributes(self):
        return self._attributes
    
    def _control(self, locator, attribute, value):
        if attribute == _attr_intensity:
            if value != 0:
                cmd = InsteonMessage(InsteonMessage.DIRECT_CMD, 0x12, value)
            else:
                cmd = InsteonMessage(InsteonMessage.DIRECT_CMD, 0x14, 0)
            locator.domain._sendmsg(locator.address, cmd)
        else:
            raise ValueError(b"Unexpected attribute received")
    
    def _dispatch(self, src, dest, msg):
        pass
    
    @property
    def identifier(self):
        return "power_dimmable"
    
    def _interrogate(self, locator, attribute):
        if attribute == _attr_intensity:
            raise NotImplementedError()
        else:
            raise ValueError(b"Unexpected attribute received")
