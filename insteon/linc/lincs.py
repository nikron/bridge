"""
Convience way to set objects with INSTEON command bytes and products.
"""
from insteon.command.command_bytes_util import CommandBytesMap

from collections import defaultdict

class LincMap():
    """
    The purpose of this class is to be able to map
    command bytes of insteon commands + a product name or (subcat/cat)
    to an object that is unique to that key.

    :param call: Whether to call partially matched cmds with the object instead of returning it.
    :type call: bool
    """

    def __init__(self, call = True):
        self.call = call
        self.products = defaultdict(lambda : [None , CommandBytesMap(self.call)])

    def register_with_product(self, name, obj):
        """
        Register an object with a product.
        """
        self.products[name][0] = obj

    def register_with_command(self, name, cmd, obj, relative_cmd = None):
        """
        Register an object with a product + command byte combo.
        """
        self.products[name][1].register(cmd, obj, relative_cmd)

    def get_with_product(self, name):
        """
        Get the object registered with a prodcut.
        """
        return self.products[name][0]

    def get_with_command(self, name, command, relative_cmd = None):
        """
        Get the object registered with a product + command combo.
        """
        return self.products[name][1].get(command, relative_cmd)

    @staticmethod
    def product_names():
        """
        List of known products.
        """
        return list(LIST_OF_LINCS.keys())

LIST_OF_LINCS = {
        'ApplianceLinc V2' : (b'\x02', b'\x09'),
        'DimmerLinc V2' : (b'\x01', b'\x00')
        }
