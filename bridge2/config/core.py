from __future__ import absolute_import, division, print_function, unicode_literals
import abc
import collections
import yaml
import bridge2.config.eyaml as eyaml

#
# Configuration object base classes
#

class ConfigurationObject(object):
    __metaclass__ = abc.ABCMeta
    
    @classmethod
    def fromconfig(cls, cnode):
        raise NotImplementedError()
        
    @abc.abstractmethod
    def toconfig(self):
        pass
        
    @classmethod
    def _yamlconstruct(cls, loader, node):
        fields = loader.construct_mapping(node)
        anchor = node.anchor if hasattr(node, b"anchor") else None
        # TODO: Validate identifier
        cnode = ConfigurationNode(fields, anchor)
        # TODO: Get ds from somewhere
        return cls.fromconfig(ds, cnode)
        
    @classmethod
    def _yamlrepresent(cls, dumper, data):
        cnode = data.toconfig()
        assert isinstance(cnode, ConfigurationNode)
        node = dumper.represent_mapping(cls.__name__, cnode._fields)
        return node

class ConfigurationEntity(ConfigurationObject):
    @abc.abstractproperty
    def identifier(self):
        pass
    
    @classmethod
    def _yamlconstruct(cls, loader, node):
        fields = loader.construct_mapping(node)
        if not hasattr(node, b"anchor"):
            fmt = b"Entity type '{0}' requires an identifier"
            raise ValueError(fmt.format(cls.__name__))
        identifier = node.anchor
        # TODO: Validate identifier
        cnode = ConfigurationNode(fields, identifier)
        # TODO: Get ds from somewhere
        return cls.fromconfig(cnode)
        
    @classmethod
    def _yamlrepresent(cls, dumper, data):
        cnode = data.toconfig()
        assert isinstance(cnode, ConfigurationNode)
        node = dumper.represent_mapping(cnode._fields)
        node.anchor = data.identifier
        return node

#
# Configuration representation
#

class ConfigurationNode(object):
    def __init__(self, fields={}, identifier=None):
        assert isinstance(fields, dict)
        self.identifier = identifier
        self._fields = fields
    
    def consumed(self):
        if len(self._fields) != 0:
            k0, _ = self._fields.popitem()
            raise Exception(b"Field '{0}' not expected".format(k0))
    
    @property
    def identifier(self):
        return self._identifier
    
    @identifier.setter
    def identifier(self, rhs):
        assert rhs == None or isinstance(rhs, unicode)
        self._identifier = rhs
    
    def pop(self, key, cls, optional=False):
        assert isinstance(key, unicode)
        assert isinstance(cls, type)
        assert isinstance(optional, bool)
        value = self._fields.get(key)
        if value == None and not optional:
            raise KeyError(b"Required field '{0}' does not exist".format(key))
        elif value != None:
            if not isinstance(value, cls):
                raise KeyError(b"Unexpected type for field '{0}'".format(key))
            del self._fields[key]
        return rv
    
    def push(self, key, value):
        assert isinstance(key, unicode)
        assert key not in self._fields
        if value == None:
            return
        self._fields[key] = value

class ConfigurationDataSet(object):
    def __init__(self, etypes, src=None):
        self._prepyaml(etypes)
        self._entities = collections.OrderedDict.fromkeys(etypes, {})
        
    def _prepyaml(self, etypes):
        # Register the specified entity types for this instance only
        # HACK: This is extremely inelegant
        assert all((issubclass(t, ConfigurationEntity) for t in etypes))
        self._reps = yaml.SafeRepresenter.yaml_representers.copy()
        self._ctors = yaml.SafeConstructor.yaml_constructors.copy()
        for etype in etypes:
            self._reps[etype] = cls._yamlrepresent
            self._ctors[etype.__name__] = cls._yamlconstruct

    def load(self, src):
        loader = eyaml.ESafeLoader(src)
        try:
            loader.yaml_constructors = self._ctors
            data = None
            if loader.check_data():
                data = loader.get_data();
            if data == None or loader.check_data():
                raise IOError(b"Expected exactly one configuration document")
            if not isinstance(data, list):
                raise IOError(b"Incorrect configuration structure")
            for etype, edict in self._entities:
                self._entities[etype] = {}
            for ent in data:
                self._entities[etype][ent.identifier] = ent
        finally:
            loader.dispose()

    def save(self, dest):
        dumper = eyaml.ESafeDumper(dest)
        try:
            dumper.yaml_representers = self._reps
            dumper.open()
            egen = (d.itervalues() for d in self._entities.itervalues())
            ents = list(itertools.chain(egen))
            dumper.represent(ents)
            dumper.close()
        finally:
            dumper.dispose()
