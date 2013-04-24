from insteon_protocol.command.command_bytes_util import CommandBytesMap
from insteon_protocol.command.command_bytes import *

from collections import defaultdict

class LincMap():
    """The purpose of this class is to be able to map
    command bytes of insteon commands + a product name or (subcat/cat)
    to an object that is unique to that key."""


    def __init__(self, call = True):
        self.call = call
        self.products = defaultdict(lambda : [None , CommandBytesMap(self.call)])

    def register_with_product(self, name, obj):
        self.products[name][0] = obj

    def register_with_command(self, name, cmd, obj, relative_cmd = None):
        self.products[name][1].register(cmd, obj, relative_cmd)

    def get_with_product(self, name):
        return self.products[name][0]

    def get_with_command(self, name, command, relative_cmd = None):
            return self.products[name][1].get(command, relative_cmd)

    def names(self):
        return list(LIST_OF_LINCS.keys())

LIST_OF_LINCS = {
        'ApplianceLinc V2' : (b'\x02', b'\x09')
        }
