from bridge.services.io.devcore import DeviceProfile
from bridge.services.model.attributes import Attribute, IntegerSpace

class DimmablePowerDeviceProfile(DeviceProfile):
    _attributes = [
        Attribute("intensity", IntegerSpace(0, 0xFF))
    ]
    
    @property
    def attributes(self):
        pass
    
    def control(self, locator, attribute, value)
        pass
        
    @property
    def identifier(self):
        return "dimmable_power"
    
    def interrogate(self, locator, attribute)
        pass
