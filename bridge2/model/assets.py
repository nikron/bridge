from __future__ import absolute_import, division, print_function, unicode_literals
import gevent
import gevent.coros
import gevent.event
from bridge2.config.config import ConfigurableEntity
from bridge2.io.devices import DeviceProfile, Locator

class Asset(ConfigurableEntity):
    """Represents a unit of equipment accessible on a Domain."""
    def _CacheEntry(object):
        def __init__(self):
            self.cval = None
            self.pval = None
            self.ts = None
            self.lock = gevent.coros.RLock()
    
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
        self._cache = {}

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
    
    def _doquery(self, attribute, ce):
        # Interrogate the device
        val = self._device.interrogate(attribute)
        
        # Produce a cache entry and return
        if attribute.cacheable:
            ce.cval = val
            ce.ts = time.time()
        return val
    
    def _doupdate(self, attribute, value, ce):
        # Control the device
        ce.lock.acquire()
        self._device.control(attribute, value)
        ce.pval = None
        ce.lock.release()
        
        # Update the cache if necessary
        if attribute.writable and attribute.cacheable:
            ce.cval = value
        return value
    
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

    def query(self, attribute, max_staleness=0.0, pending=False):
        return self._query(attribute, max_staleness, pending, False)
    
    def _query(self, attribute, max_staleness, pending, async):
        # Validate arguments
        assert isinstance(attribute, Attribute)
        if not attribute.readable:
            raise ValueError("The specified attribute is not readable")
        if pending and not attribute.writable:
            raise ValueError("Read-only attributes cannot have pending values")
            
        # Retrieve the result from cache if possible
        rv = None
        ce = self._cache.get(attribute.identifier)
        if ce != None:
            if pending and ce.pval != None:
                rv = ce.pval
            elif attribute.cacheable:
                cts = time.time()
                if (cts - ce.ts) < max_staleness:
                    rv = ce.cval
        else:
            ce = _CacheEntry()
            self._cache[attribute.identifier] = ce
        
        # Finish the job and return
        if not async:
            if rv != None:
                return rv
            return self._doquery(attribute, ce)
        ar = gevent.event.AsyncResult()
        if rv != None:
            ar.set(rv)
        else:
            gevent.spawn(self._doquery, self, attribute, ce).link(ar)
        return ar
        
    def query_async(self, attribute, max_staleness=0.0, pending=False):
        return self._query(attribute, max_staleness, pending, True)

    def update(self, attribute, value):
        return self._update(attribute, value, False)
        
    def _update(self, attribute, value, async):
        # Validate arguments
        assert isinstance(attribute, Attribute)
        if not attribute.writable:
            raise ValueError("The specified attribute is not writable")
        if not attribute.space.validate(value):
            raise ValueError("Illegal attribute value")
            
        # Retrieve the cache entry
        ce = self._cache.get(attribute.identifier)
        if ce == None:
            ce = _CacheEntry()
            self._cache[attribute.identifier] = ce
        ce.pval = value
        
        # Finish the job and return
        if async:
            ar = gevent.event.AsyncResult()
            gevent.spawn(self._doupdate, self, attribute, value, ce).link(ar)
            return ar
        else:
            return self._doupdate(attribute, value, ce);

    def update_async(self, attribute, value):
        return self._update(attribute, value, True)
