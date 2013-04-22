from __future__ import absolute_import, division, print_function, unicode_literals
import abc
from bridge2.io.devices import DeviceProfile

class _InsteonDeviceProfile(DeviceProfile):
    __metaclass__ = abc.ABCMeta
    
    def bind(self, locator):
        return locator.domain._bind(locator, self)
    
    @abc.abstractmethod
    def _control(self, locator, attribute, value):
        pass
        
    @abc.abstractmethod
    def _interrogate(self, locator, attribute):
        pass
