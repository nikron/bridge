"""
Idiom for model to communicate with insteon io
services.
"""
from bridge.services.model.idiom import ModelIdiom, IdiomError
from bridge.services.model.assets import BlankAsset, OnOffAsset, OnOffBacking

from insteon_protocol.command.commands import InsteonCommand
from insteon_protocol.utils import check_insteon_id


import logging
from binascii import hexlify, unhexlify
import binascii


class InsteonIdiom(ModelIdiom):
    """
    Decipher InsteonCommand objects.
    """

    def create_onoff(self, real_id, name):
        """Create the onoff assets."""
        def turn_on():
            self.service_function('turn_on', hexlify(real_id))

        def turn_off():
            self.service_function('turn_off', hexlify(real_id))

        return OnOffAsset(name, OnOffBacking(real_id, turn_on, turn_off))

    def create_asset(self, name, real_id, asset_class):
        if type(real_id) == str:
            try:
                check = unhexlify(real_id)
            except binascii.Error:
                raise IdiomError("Could not unhexlify `{0}`.".format(real_id))

            if not check_insteon_id(check):
                raise IdiomError("Insteon ID's ore byte string of length 3.")

        try:
            create_func = ASSET_TYPES[asset_class]
        except AttributeError:
            raise IdiomError("Invalid asset class.")

        asset = create_func(self, real_id, name)

        return asset


    def guess_insteon_asset(self, command):
        """
        We know it is an insteon command, let's try to guess what kind of device
        it corresponds to.
        """
        cmd1 = command.cmd1
        cmd2 = command.cmd2

        if cmd1 == b'\x03' and cmd2 == b'\x00':
            logging.debug("Found a product description command with extended data: {0}.".format(
                repr(command.extended_data)))

        return (BlankAsset(command.from_address), False)

    def guess_asset(self, real_id, update):
        if issubclass(type(update), InsteonCommand):
            return self.guess_insteon_asset(update)
        else:
            return (BlankAsset(real_id), False)


    def get_state(self, real_id, update):
        pass

    def asset_types(self):
        return list(ASSET_TYPES.keys())

ASSET_TYPES = { 'ApplianceLinc V2' : InsteonIdiom.create_onoff }
