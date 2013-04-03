"""
Idiom for model to communicate with insteon io
services.
"""
from bridge.services.model.idiom import ModelIdiom, IdiomError
from bridge.services.model.assets import BlankAsset, OnOffAsset, OnOffBacking

from insteon_protocol.command.commands import InsteonCommand
from insteon_protocol.command.command_bytes import *
from insteon_protocol.command.command_bytes_util import CommandBytesMap
from insteon_protocol.utils import check_insteon_id


import logging
from binascii import unhexlify
import binascii


class InsteonIdiom(ModelIdiom):
    """
    Decipher InsteonCommand objects.
    """

    def create_onoff(self, name, real_id, product_name):
        """Create the onoff assets."""
        def turn_on():
            self.service_function('turn_on', real_id)

        def turn_off():
            self.service_function('turn_off', real_id)

        return OnOffAsset(name, OnOffBacking(real_id, product_name, turn_on, turn_off))

    def create_asset(self, name, real_id, product_name):
        if type(real_id) == str:
            try:
                check = unhexlify(real_id) #make sure string is valid
            except binascii.Error:
                raise IdiomError("Could not unhexlify `{0}`.".format(real_id))

            if not check_insteon_id(check):
                raise IdiomError("Insteon ID's are byte string of length 3.")

        try:
            create_func = PRODUCT_NAMES[product_name]
        except AttributeError:
            raise IdiomError("Invalid asset class.")

        asset = create_func(self, name, real_id, product_name)

        return asset


    def guess_insteon_asset(self, real_id, command):
        """
        We know it is an insteon command, let's try to guess what kind of device
        it corresponds to.
        """
        cmd1 = command.cmd1
        cmd2 = command.cmd2

        if cmd1 == b'\x03' and cmd2 == b'\x00':
            logging.debug("Found a product description command with extended data: {0}.".format(
                repr(command.extended_data)))

        return (BlankAsset(real_id), False)

    def guess_asset(self, real_id, update):
        if issubclass(type(update), InsteonCommand):
            return self.guess_insteon_asset(real_id, update)
        else:
            return (BlankAsset(real_id), False)

    def get_state(self, real_id, update):
        #if issubclass(type(update), InsteonCommand):
        try:
            return INSTCMDTOSTATE.get(update)
        except KeyError:
            raise IdiomError("Update not implemented.")


    def asset_product_names(self):
        return list(PRODUCT_NAMES.keys())

PRODUCT_NAMES = { 'ApplianceLinc V2' : InsteonIdiom.create_onoff }

INSTCMDTOSTATE = CommandBytesMap()
INSTCMDTOSTATE.register(TURNONFAST, ('main', 'on'))
INSTCMDTOSTATE.register(TURNOFF, ('main', 'off'))
