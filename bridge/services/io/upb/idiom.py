from bridge.services.model.idiom import ModelIdiom, IdiomError
from bridge.services.model.assets import OnOffAsset

from upb import mdid, registers, UPBMessage
from upb.device_info import UPBDeviceInfo

PLACEHOLDER = "upb"

class UPBIdiom(ModelIdiom):
    def create_asset(self, name, real_id, product_name):
        raise IdiomError("Doesn't create assets.")

    def change_state(self, asset, update):
        if issubclass(type(update), UPBMessage):
            changer = MDID_CHANGERS[update.MDID]
            if changer is not None:
                changer(asset, update)
        elif type(update) is UPBDeviceInfo:
            asset.name = update.rname.strip().decode() + ' ' + update.dname.strip().decode()
        else:
            logging.debug("Didn't recognize update.")

    def guess_asset(self, real_id, update):
        new_asset = OnOffAsset("", real_id, self.service, PLACEHOLDER)
        self.change_state(new_asset, update)
        return new_asset, False

    def product_names(self):
        return [PLACEHOLDER]

def change_main_level(asset, update):
    if update.arguments[0] > 0:
        asset.transition('main', True)
    else:
        asset.transition('main', False)

MDID_CHANGERS = [None for _ in range(0, 0x94)]
MDID_CHANGERS[mdid.DEVICE_STATE] = change_main_level
MDID_CHANGERS[mdid.GOTO] = change_main_level
