from __future__ import absolute_import, division, print_function, unicode_literals
import abc

#
# Attribute spaces
#

class Space(object):
    """Represents a range of possible values for an Attribute."""
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractproperty
    def parameters(self):
        """Return the parameters defining this Space."""
        pass
    
    @abc.abstractmethod
    def validate(self, value):
        """Determine whether a value is within this Space."""
        pass

class NullSpace(Space):
    """Enables the definition of a valueless Attribute (in other words, a
       one-shot operation)."""
    @property
    def parameters(self):
        return {}
    
    def validate(self, value):
        return value == None

class BooleanSpace(Space):
    """Represents the range of possible values for a boolean Attribute."""
    @property
    def parameters(self):
        return {}
    
    def validate(self, value):
        return isinstance(value, bool)

class IntegerSpace(Space):
    """Represents the range of possible values for an integer Attribute."""
    def __init__(self, min_value, max_value):
        assert isinstance(min_value, int)
        assert isinstance(max_value, int)
        self.min_value = min_value
        self.max_value = max_value
    
    @property
    def parameters(self):
        return {"min_value": min_value, "max_value": max_value}
    
    def validate(self, value):
        if not isinstance(value, int):
            return False
        if value < self.min_value or value > self.max_value:
            return False
        return True

#
# Attributes
#

class Attribute(object):
    """Represents a feature of a controllable element that may be accessed or
       controlled."""
    def __init__(self, identifier, space, readable=True, writable=True, cacheable=None, config=False):
        if cacheable == None:
            cacheable = readable
        assert isinstance(identifier, unicode)
        assert isinstance(space, Space)
        assert isinstance(readable, bool)
        assert isinstance(writable, bool)
        assert isinstance(cacheable, bool)
        assert isinstance(config, bool)
        assert readable or not cacheable
        self._identifier = identifier
        self._space = space
        self._readable = readable
        self._writable = writable
        self._cacheable = cacheable
        self._config = config

    @property
    def cacheable(self):
        """Return whether or not this Attribute is cacheable."""
        return self._cacheable

    @property
    def config(self):
        """Return whether or not this Attribute is a configuration feature."""
        return self._config

    @property
    def identifier(self):
        """Return the identifier for this Attribute."""
        return self._identifier
    
    @property
    def readable(self):
        """Return whether or not this Attribute is readable."""
        return self._readable
    
    @property
    def space(self):
        """Return the space for the values of this Attribute."""
        return self._space
        
    @property
    def writable(self):
        """Return whether or not this Attribute is writable."""
        return self_.writable
