from bridge.services.model.idiom import ModelIdiom, IdiomError
from bridge.services.model.assets import OnOffAsset

from upb import mdid, registers

PLACEHOLDER = "upb"

class UPBIdiom(ModelIdiom):
    def create_asset(self, name, real_id, product_name):
        raise IdiomError("Doesn't create assets.")

    def change_state(self, asset, update):
        changer = MDID_CHANGERS[update.MDID]
        if changer is not None:
            changer(asset, update)

    def guess_asset(self, real_id, update):
        return OnOffAsset("", real_id, self.service, PLACEHOLDER), False

    def product_names(self):
        return [PLACEHOLDER]

def change_main_level(asset, update):
    if update.arguments[0] > 0:
        asset.transition('main', True)
    else:
        asset.transition('main', False)

DeviceName = registers.RegisterDescription(registers.DNAME)
RoomName = registers.RegisterDescription(registers.RNAME)
def set_information(asset, update):
    if RoomName.is_report(update):
        asset.name =  RoomName.make_string(update)

MDID_CHANGERS = [None for _ in range(0, 0x94)]
MDID_CHANGERS[mdid.DEVICE_STATE] = change_main_level
MDID_CHANGERS[mdid.GOTO] = change_main_level
MDID_CHANGERS[mdid.REGISTER_VALUES] = set_information
