import abc
from bridge2.io.devices import Domain
from bridge2.model.assets import Asset

class ConfigurableEntity(object):
    __metaclass__ = abc.ABCMeta
    
    @classmethod
    def fromconfig(cls, sect):
        pass
        
    @abc.abstractmethod
    def toconfig(self):
        pass

class ConfigurationSection(object):
    def consume(self, key):
        pass
        
    @property
    def dataset(self):
        return self._dataset

class ConfigurationDataSet(ConfigurableEntity):
    def __init__(self):
        types = [Asset, Domain]
        self._entities = dict.fromkeys(types, [])
    
    @classmethod
    def fromconfig(cls, sect):
        pass

    def resolve(self, cls, identifier):
        pass

    def toconfig(self):
        pass
