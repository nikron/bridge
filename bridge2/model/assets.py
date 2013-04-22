from __future__ import absolute_import, division, print_function, unicode_literals
from bridge2.io.devices import DeviceProfile, Locator

class Asset(object):
    """Represents a unit of equipment accessible on a Domain."""
    def __init__(self, identifier, locator, profile, display_name):
        assert isinstance(identifier, unicode)
        assert isinstance(locator, Locator)
        assert isinstance(profile, DeviceProfile)
        assert isinstance(display_name, unicode)
        self._identifier = identifier
        self._locator = locator
        self._profile = profile
        self._display_name = display_name
        self._device = profile.bind(locator)

    @property
    def attributes(self):
        """Return a list of attributes valid against this Asset."""
        return self._profile.attributes
        
    @property
    def display_name(self):
        """Return the display name for this Asset."""
        return self._display_name

    @display_name.setter
    def display_name(self, rhs):
        assert isinstance(rhs, unicode)
        # FIXME: Do validity checking
        self._display_name = rhs
        
    @property
    def identifier(self):
        """Return the identifier for this Asset."""
        return self._identifier
        
    @property
    def locator(self):
        """Return the Locator of this Asset."""
        return self._locator    
    
    @property
    def profile(self):
        """Return the DeviceProfile assigned to this Asset."""
        return self._profile

    def query(self, attribute, max_staleness=0):
        assert isinstance(attribute, Attribute)
        raise NotImplementedError()
        
    def query_async(self, attribute, max_staleness=0):
        assert isinstance(attribute, Attribute)
        raise NotImplementedError()

    def update(self, attribute, value):
        assert isinstance(attribute, Attribute)
        raise NotImplementedError()
        
    def update_async(self, attribute, value):
        assert isinstance(attribute, Attribute)
        raise NotImplementedError()
