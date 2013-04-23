import abc
import yaml

class ConfigurableEntity(object):
    __metaclass__ = abc.ABCMeta
    
    @classmethod
    def fromconfig(cls, sect):
        raise NotImplementedError()
        
    @abc.abstractmethod
    def toconfig(self):
        pass

class ConfigurationSection(object):
    def consume(self, key, optional=False):
        assert isinstance(key, unicode)
        assert isinstance(optional, bool)
        value = self._fields.get(key)
        if value == None and not optional:
            raise KeyError("Required field {0} does not exist".format(key))
        elif value != None:
            del self._fields[key]
        return rv
    
    def consumed(self):
        if len(self._fields) != 0:
            k0, _ = self._fields.popitem()
            raise Exception("Unrecognized field {0} encountered".format(k0))
    
    @property
    def dataset(self):
        return self._dataset

class ConfigurationDataSet(ConfigurableEntity):
    def __init__(self, rtypes):
        assert all((isinstance(t, type) for t in rtypes))
        self._entities = dict.fromkeys(rtypes, {})
        self._tmpentities = dict.fromkeys(rtypes, {})
    
    @classmethod
    def fromconfig(cls, sect):
        pass

    def resolve(self, cls, identifier):
        # Validate arguments
        assert isinstance(cls, type)
        assert isinstance(identifier, unicode)
        
        # Check if we've already decoded the entity
        ents = self._entities.get(cls)
        if ents == None:
            raise ValueError("The specified type is not a root-level entity")
        rv = ents.get(identifier)
        if rv != None:
            return rv
            
        # Check if we have a section representing the entity
        tents = self._tmpentities[target]
        sect = tents.get(identifier)
        if sect == None:
            raise KeyError("The specified entity does not exist")
        
        # Drop the section to prevent circular resolution
        del tents[identifier]
        
        # Decode, store, and return the entity
        rv = cls.fromconfig(sect)
        ents[identifier] = rv
        return rv

    def toconfig(self):
        pass
