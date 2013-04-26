from __future__ import absolute_import, division, print_function, unicode_literals
from ..attributes import *
from ..devices import *

class InsteonDeviceProfile(DeviceProfile):
    def bind(self, locator):
        from .domain import InsteonDomain
        assert isinstance(locator, Locator)
        assert isinstance(locator.domain, InsteonDomain)
        return locator.domain._bind(locator, self)
    
    @abc.abstractmethod
    def _control(self, locator, attribute, value):
        pass
        
    @abc.abstractmethod
    def _dispatch(self, src, dest, msg):
        pass
        
    @abc.abstractmethod
    def _interrogate(self, locator, attribute):
        pass

class InsteonDeviceRef(DeviceRef):
    def __init__(self, locator, profile):
        assert isinstance(profile, InsteonDeviceProfile)
        super(InsteonDeviceRef, self).__init__(locator, profile)
        self._subscriber = None
    
    def control(self, attribute, value):
        # Validate arguments
        assert isinstance(attribute, Attribute)
        if not attribute in self.profile.attributes:
            raise ValueError(b"Only attributes of this device are permitted")
        if not attribute.writable:
            raise ValueError(b"The specified attribute is not writable")
        if not attribute.space.validate(value):
            raise ValueError(b"Illegal attribute value")
            
        # Delegate to the profile
        addr = self.locator.address
        return self.profile._control(addr, attribute, value)
    
    def interrogate(self, attribute):
        # Validate arguments
        assert isinstance(attribute, Attribute)
        if not attribute in self.profile.attributes:
            raise ValueError(b"Only attributes of this device are permitted")
        if not attribute.readable:
            raise ValueError(b"The specified attribute is not readable")
            
        # Delegate to the profile
        addr = self.locator.address
        return self.profile._interrogate(addr, attribute)
    
    def subscribe(self, fn):
        if self._subscriber != None:
            fn2 = self._subscriber
            def chain(evt):
                fn2(evt)
                fn(evt)
            self._subscriber = chain
        else:
            self._subscriber = fn
