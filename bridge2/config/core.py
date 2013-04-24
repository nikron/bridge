from __future__ import absolute_import, division, print_function, unicode_literals
import abc
import itertools
import yaml
import yaml.constructor
import yaml.representer
import bridge2.config.eyaml as eyaml

#
# Configuration object base classes
#

class ConfigurationObject(object):
    __metaclass__ = abc.ABCMeta
    
    @classmethod
    def _fromconfig(cls, cnode):
        raise NotImplementedError()
        
    @abc.abstractmethod
    def _toconfig(self):
        pass
        
    @classmethod
    def _yamlconstruct(cls, loader, node):
        fields = loader.construct_mapping(node)
        # TODO: Validate identifier
        cnode = ConfigurationNode(None, fields)
        # TODO: Get ds from somewhere
        return cls._fromconfig(cnode)
        
    @classmethod
    def _yamlrepresent(cls, dumper, data):
        cnode = data._toconfig()
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
        cnode = ConfigurationNode(identifier, fields)
        # TODO: Get ds from somewhere
        return cls._fromconfig(cnode)
        
    @classmethod
    def _yamlrepresent(cls, dumper, data):
        cnode = data._toconfig()
        assert isinstance(cnode, ConfigurationNode)
        node = dumper.represent_mapping(cls.__name__, cnode._fields)
        node.anchor = data.identifier
        return node

#
# Configuration representation
#

class ConfigurationNode(object):
    def __init__(self, identifier=None, fields=None):
        if fields == None:
            fields = {}
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
    def __init__(self, etypes):
        self._prepyaml(etypes)
        self._etypes = etypes
        self._entities = dict([(t, {}) for t in etypes])
    
    def find(self, etype, identifier):
        assert etype in self._etypes
        assert isinstance(identifier, unicode)
        edict = self._entities[etype]
        ent = edict.get(identifier)
        if ent == None:
            raise KeyError(b"The requested entity was not found")
        return ent

    def insert(self, entity):
        assert type(entity) in self._etypes
        for edict in self._entities.itervalues():
            if entity.identifier in edict:
                raise ValueError(b"The entity's identifier is already in use")
        self._entities[type(entity)][entity.identifier] = entity

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
            for etype in self._etypes:
                self._entities[etype].clear()
            for ent in data:
                edict = self._entities.get(type(ent))
                if edict == None:
                    raise IOError(b"Unexpected entity type encountered")
                edict[ent.identifier] = ent
        finally:
            loader.dispose()

    def _prepyaml(self, etypes):
        # Register the specified entity types for this instance only
        # HACK: This is extremely inelegant
        assert all((issubclass(t, ConfigurationEntity) for t in etypes))
        sr = yaml.representer.SafeRepresenter
        sc = yaml.constructor.SafeConstructor
        self._reps = sr.yaml_representers.copy()
        self._ctors = sc.yaml_constructors.copy()
        for etype in etypes:
            self._reps[etype] = etype._yamlrepresent
            self._ctors[etype.__name__] = etype._yamlconstruct

    def remove(self, entity):
        assert type(entity) in self._etypes
        try:
            del self._entities[type(entity)][entity.identifier]
        except:
            raise KeyError(b"The specified entity was not found")

    def save(self, dest):
        dumper = eyaml.ESafeDumper(dest, default_flow_style=False)
        try:
            dumper.yaml_representers = self._reps
            dumper.open()
            egen = (d.values() for d in self._entities.itervalues())
            ents = list(itertools.chain(*egen))
            dumper.represent(ents)
            dumper.close()
        finally:
            dumper.dispose()
