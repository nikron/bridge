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
        asset.change("Network ID", device_info.nid)
        asset.change("Unit ID", device_info.uid)
        asset.change("Network Password", device_info.npw)
        asset.change("UBP Options", device_info.ubop)
        asset.change("UBP Version", device_info.upbver)
        asset.change("Manufacture ID", device_info.mid)
        asset.change("Product ID", device_info.pid)
        asset.change("Firmware Version", device_info.fwver)
        asset.change("Serial Number", device_info.sernum)
        asset.change("Network Name", device_info.nname)
        asset.change("Room Name", device_info.rname)
        asset.change("Device Name", device_info.dname)

def change_main_level(asset, update):
    level = update.arguments[0]
    asset.change("main", level > 0)
    asset.change("Level", level)


MDID_CHANGERS = [None for _ in range(0, 0x94)]
MDID_CHANGERS[mdid.DEVICE_STATE] = change_main_level
MDID_CHANGERS[mdid.GOTO] = change_main_level
