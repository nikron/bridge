from bridge.services.io.devices import DeviceProfile
from bridge.services.io.insteon.devices import InsteonDeviceProfile
from bridge.services.model.attributes import Attribute, IntegerSpace
from insteon_protocol.command import im_commands

class DimmablePowerDeviceProfile(InsteonDeviceProfile):
    _alist = [
        Attribute("intensity", IntegerSpace(0, 0xFF))
    ]
    _amap = {a.identifier: a for a in _alist}
    
    @property
    def attributes(self):
        return self._alist
    
    def _control(self, locator, attribute, value)
        # Produce a command
        if attribute.identifier == "intensity":
            cmd = im_commands.TurnOnFast(real_id) # FIXME: Wrong command
            
        # Transmit it
        locator.domain._xmit(locator.address, cmd)
    
    def find_attribute(self, identifier):
        return self._amap.get(identifier)
    
    @property
    def identifier(self):
        return "dimmable_power"
    
    def _interrogate(self, locator, attribute)
        raise NotImplementedError()
