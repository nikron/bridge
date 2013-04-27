"""
Idiom for model to communicate with insteon IO services.
"""
from bridge.services.model.idiom import ModelIdiom, IdiomError
from bridge.services.model.assets import BlankAsset, OnOffAsset, DimmerAsset

from insteon_protocol.command.command_bytes import TURNONFAST, TURNOFF, LIGHTSTATUSREQUEST, TURNONLEVEL
from insteon_protocol.linc.lincs import LincMap
from insteon_protocol.utils import check_insteon_id

import logging
from binascii import unhexlify
import binascii

class InsteonIdiom(ModelIdiom):
    """
    Decipher :class:`InsteonIMUpdate` objects into asset transitions, or whole
    assets.
    """

    def create_asset(self, name, real_id, product_name):
        """
        Create an asset out of minimum posible information.
        Since http service can't know for sure if a given ID is correct
        for a IO service, must check here.

        :param name: Name of the asset.
        :type name: str

        :param real_id: Real id of the insteon device.
        :type real_id: str

        :param product_name: Product name of the insteon device.
        :type product_name: str

        :return: The initialized asset
        :rtype: :class:`Asset`
        """
        if isinstance(real_id, str):
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

    def create_onoff(self, name, real_id, product_name):
        """
        Create an :class:`OnOffAsset`.

        :param name: Name of the asset.
        :type name: str

        :param real_id: Real ID of the asset.
        :type real_id: str

        :param product_name: Product name of the asset.
        :type product_name: str

        :return: An initialized OnOffAsset with an unknown state.
        :rtype: :class:`OnOffAsset`
        """
        return OnOffAsset(name, real_id, self.service, product_name)

    def create_dimmer(self, name, real_id, product_name):
        """
        Create an :class:`DimmerAsset`.

        :param name: Name of the asset.
        :type name: str

        :param real_id: Real ID of the asset.
        :type real_id: str

        :param product_name: Product name of the asset.
        :type product_name: str

        :return: An initialized :class:`DimmerAsset` with an unknown state.
        :rtype: :class:`OnOffAsset`
        """
        return DimmerAsset(name, real_id, self.service, product_name)

    def change_state(self, asset, update):
        """
        Change the state of the update using an update, looks into a mapping
        of command bytes to tuples to find a transition.

        :param asset: Update from Insteon IO service
        :type asset: :class`InsteonIMUpdate`
        """
        try:
            category, state = LINCMAPPING.get_with_command(asset.get_product_name(), update.command, update.relative)
            asset.transition(category, state)

        except KeyError:
            raise IdiomError("Update not implemented.")

    def guess_asset(self, real_id, update):
        """
        We currently don't guess assets, just return blank assets.

        :param real_id: Real ID of insteon device.
        :type real_id: str

        :param update: A random InsteonUpdate, could be anything.
        :type update: :class:`InsteonIMUpdate`

        :return: The guessed initialized asset.
        :rtype: :class:`BlankAsset`
        """
        return BlankAsset(real_id, self.service), False

    def product_names(self):
        """
        Product names associated with IO service/idiom.

        :return: List of strings of the available Products.
        :rtype: [str]
        """
        return LINCMAPPING.names()

LINCMAPPING = LincMap()
LINCMAPPING.register_with_product('ApplianceLinc V2', InsteonIdiom.create_onoff)
LINCMAPPING.register_with_product('DimmerLinc V2', InsteonIdiom.create_dimmer)

def bytes_to_range(cmd_bytes):
    return 'main', int(cmd_bytes.cmd1)

LINCMAPPING.register_with_command('DimmerLinc V2', TURNONLEVEL, bytes_to_range)

LINCMAPPING.register_with_command('ApplianceLinc V2', TURNONFAST, ('main', True))
LINCMAPPING.register_with_command('ApplianceLinc V2', TURNOFF, ('main', False))

def bytes_to_bool(cmd_bytes):
    """
    LincMap will call this function on a range of command bytes.

    :param cmd_bytes: Bytes object to find a state transition from
    :type cmd_byts: CMDS

    :return: A tuple representing a state transition
    :rtype: (str, bool)
    """
    logging.debug("Using the to figure out status requests.")
    if cmd_bytes.cmd2 == 0:
        return 'main', False
    else:
        return 'main', True

LINCMAPPING.register_with_command('ApplianceLinc V2', LIGHTSTATUSREQUEST, bytes_to_bool)
