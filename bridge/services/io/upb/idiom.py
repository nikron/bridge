from bridge.services.model.idiom import ModelIdiom, IdiomError
from bridge.services.model.assets import OnOffAsset

from upb import mdid

PLACEHOLDER = "upb"

class UPBIdiom(ModelIdiom):
    def create_asset(self, name, real_id, product_name):
        raise IdiomError("Doesn't create assets.")

    def change_state(self, asset, update):
        changer = MDID_CHANGERS[update.MDID]
        if changer is not None:
            changer(asset, update)

    def guess_asset(self, real_id, update):
        return OnOffAsset("", real_id, self.service, PLACEHOLDER), True

    def product_names(self):
        return [PLACEHOLDER]

MDID_CHANGERS = [None for _ in range(0, 0x94)]

def change_main_level(asset, update):
    asset.transition('main', update.arguments[0])

MDID_CHANGERS[mdid.REPORT_STATE] = change_main_level
