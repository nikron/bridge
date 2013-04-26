from __future__ import absolute_import, division, print_function, unicode_literals
from bridge2.io.devices import DeviceProfile
from bridge2.io.insteon.profiles.base import InsteonDeviceProfile
from bridge2.model.attributes import Attribute, BooleanSpace

class PowerDeviceProfile(InsteonDeviceProfile):
    _alist = [
        Attribute("power", BooleanSpace())
    ]
    _amap = {a.identifier: a for a in _alist}
    
    @property
    def attributes(self):
        return self._alist
    
    def _control(self, locator, attribute, value):
        # Produce a command
        if attribute.identifier == "power":
            cmd = im_commands.TurnOnFast(real_id) # FIXME: Wrong command
            
        # Transmit it
        locator.domain._xmit(locator.address, cmd)
    
    def find_attribute(self, identifier):
        return self._amap.get(identifier)
    
    @property
    def identifier(self):
        return "power"
    
    def _interrogate(self, locator, attribute):
        raise NotImplementedError()
