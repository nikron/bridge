from bridge.services.io.devcore import DeviceProfile
from bridge.services.io.insteon import InsteonDomain
from bridge.services.model.attributes import Attribute, IntegerSpace
from insteon_protocol.command import im_commands

class DimmablePowerDeviceProfile(DeviceProfile):
    _alist = [
        Attribute("intensity", IntegerSpace(0, 0xFF))
    ]
    _amap = {a.identifier: a for a in _alist}
    
    @property
    def attributes(self):
        return self._alist
    
    def control(self, locator, attribute, value)
        # Validate operation
        if _amap[attribute.identifier] != attribute:
            raise ValueError("Unrecognized attribute")
        if not attribute.space.validate(value):
            raise ValueError("Illegal attribute value")
        if not isinstance(locator.domain, InsteonDomain):
            raise ValueError("Locator specified is not for an Insteon device")
        
        # Produce a command
        if attribute.identifier == "intensity":
            cmd = im_commands.TurnOnFast(real_id) # FIXME: Wrong command
            
        # Transmit it
        locator.domain.send_cmd(locator.address, cmd)
    
    @abc.abstractmethod
    def find_attribute(self, identifier):
        return self._amap.get(identifier)
    
    @property
    def identifier(self):
        return "dimmable_power"
    
    def interrogate(self, locator, attribute)
        # Validate operation
        if _amap[attribute.identifier] != attribute:
            raise ValueError("Unrecognized attribute")
        if not isinstance(locator.domain, InsteonDomain):
            raise ValueError("Locator specified is not for an Insteon device")
        raise NotImplementedError()
