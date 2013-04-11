from insteon_protocol.command.command_bytes_util import CommandBytesMap
from insteon_protocol.command.command_bytes import *

class LincMap():
    """The purpose of this class is to be able to map
    command bytes of insteon commands + a product name or (subcat/cat)
    to an object that is unique to that key."""


    def __init__(self, static=True, call=True):
        self.call = call
        self.products = {}

        if static:
            self.static_loader(LIST_OF_LINCS)

    def static_loader(self, list_of_lincs):
        """Load a list of tuples of the form (product name, category, sub category, command bytes)"""

        for name, cat, subcat, cmd_bytes in list_of_lincs:
            self.products[name] = [None, CommandBytesMap(cmd_bytes, self.call)]

    def register(self, name, obj, cmd_objs):
        self.register_with_product(name, obj)

        for cmd, cmd_obj in cmd_objs:
            self.register_with_command(name, cmd, cmd_obj)

    def register_with_product(self, name, obj):
        self.products[name][0] = obj

    def register_with_command(self, name, cmd, obj):
        self.products[name][1].register(cmd, obj)

    def get(self, name, cmd=None):
        if cmd:
            return self.products[name][1].get(cmd)
        else:
            return self.products[name][0]

    def names(self):
        return list(self.products.keys())

LIST_OF_LINCS = [
('ApplianceLinc V2', b'\x00', b'\x00', [TURNONFAST,TURNOFF])
]
