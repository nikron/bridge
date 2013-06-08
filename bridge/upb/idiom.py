from bridge.services.model.idiom import ModelIdiom, IdiomError
from bridge.upb.assets import GenericUPBAsset

from upb import mdid, registers, UPBMessage
from upb.device_info import UPBDeviceInfo
import logging

PLACEHOLDER = "generic"

class UPBIdiom(ModelIdiom):
    def create_asset(self, name, real_id, product_name):
        raise IdiomError("Doesn't create assets.")

    def change_state(self, asset, update):
        if issubclass(type(update), UPBMessage):
            changer = MDID_CHANGERS[update.MDID]
            if changer is not None:
                changer(asset, update)
        elif isinstance(update, UPBDeviceInfo):
            self._change_with_device_info(asset, update)

        else:
            logging.debug("Didn't recognize update.")

    def guess_asset(self, real_id, update):
        new_asset = GenericUPBAsset("", real_id, self.service)
        self.change_state(new_asset, update)
        return new_asset, False

    def product_names(self):
        return [PLACEHOLDER]

    @staticmethod
    def _change_with_device_info(asset, device_info):
        for attr in vars(device_info):
            asset.change(attr, getattr(device_info, attr))

def change_main_level(asset, update):
    if update.arguments[0] > 0:
        asset.change('main', True)
    else:
        asset.change('main', False)

MDID_CHANGERS = [None for _ in range(0, 0x94)]
MDID_CHANGERS[mdid.DEVICE_STATE] = change_main_level
MDID_CHANGERS[mdid.GOTO] = change_main_level
