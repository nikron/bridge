from bridge.services.io.devices import DeviceProfile
from bridge.services.model.attributes import Attribute, BooleanSpace

class PowerDeviceProfile(DeviceProfile):
    _attributes = [
        Attribute("power", BooleanSpace())
    ]
    
    @property
    def attributes(self):
        return self._attributes
    
    def control(self, locator, attribute, value)
        pass
    
    @property
    def identifier(self):
        return "power"
    
    def interrogate(self, locator, attribute)
        pass
