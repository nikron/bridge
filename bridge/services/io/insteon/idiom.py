"""
Idiom for model to communicate with insteon io
services.
"""
from bridge.services.model.idiom import ModelIdiom, IdiomError
from bridge.services.model.assets import BlankAsset, OnOffAsset

from insteon_protocol.command.commands import InsteonCommand
from insteon_protocol.command.command_bytes import *
from insteon_protocol.linc.lincs import LincMap
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

        return OnOffAsset(name, real_id, self.service, product_name)

    def create_asset(self, name, real_id, product_name):
        if type(real_id) == str:
            try:
                check = unhexlify(real_id.encode()) #make sure string is valid
            except binascii.Error:
                raise IdiomError("Could not unhexlify `{0}`.".format(real_id))

            if not check_insteon_id(check):
                raise IdiomError("Insteon ID's are byte string of length 3.")

        try:
            create_func = LINCMAPPING.get_with_product(product_name)
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

        return (BlankAsset(real_id, self.service), False)

    def guess_asset(self, real_id, update):
        if issubclass(type(update), InsteonCommand):
            return self.guess_insteon_asset(real_id, update)
        else:
            return (BlankAsset(real_id, self.service), False)

    def change_state(self, asset, update):
        try:
            (category, status) = LINCMAPPING.get_with_command(asset.get_product_name(), update.command, update.relative)
            asset.transition(category, status)

        except KeyError:
            raise IdiomError("Update not implemented.")

    def product_names(self):
        return LINCMAPPING.names()

LINCMAPPING = LincMap()
LINCMAPPING.register_with_product('ApplianceLinc V2', InsteonIdiom.create_onoff)
LINCMAPPING.register_with_command('ApplianceLinc V2', TURNONFAST, ('main', True))
LINCMAPPING.register_with_command('ApplianceLinc V2', TURNOFF, ('main', False))
