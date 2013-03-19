"""
Idiom for model to communicate with insteon io
services.
"""
from bridge.services.model.idiom import ModelIdiom
from bridge.services.model.assets import BlankAsset, OnOffAsset
from bridge.services.model.states import Trigger 

from insteon_protocol.command.commands import InsteonCommand

import logging


class InsteonIdiom(ModelIdiom):
    """
    Decipher InsteonCommand objects.
    """


    def create_onoff(self, real_id, name):
        def turn_on():
            self.service_function.turn_on(real_id)

        def turn_off():
            self.service_function.turn_off(real_id)


    def create_asset(self, real_id, name, asset_type):
        create_func = ASSET_TYPES[asset_type]

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
