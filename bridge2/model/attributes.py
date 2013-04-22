import abc

#
# Attribute spaces
#

class Space(metaclass=abc.ABCMeta)
    """Represents a range of possible values for an attribute."""
    
    @abc.abstractproperty
    def parameters(self):
        """Return the parameters defining this attribute space."""
        pass
    
    @abc.abstractmethod
    def validate(self, value):
        """Determine whether a value is within this attribute space."""
        pass

class BooleanSpace(Space):
    """Represents the range of possible values for a boolean attribute."""
    
    @property
    def parameters(self):
        return {}
    
    def validate(self, value):
        return isinstance(value, bool)

class IntegerSpace(Space):
    """Represents the range of possible values for an integer attribute."""
    
    def __init__(self, min_value, max_value):
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

class Attribute():
    """Represents a feature of an asset that may be accessed or controlled."""
    
    def __init__(self, identifier, space):
        self.identifier = identifier
        self.space = space
