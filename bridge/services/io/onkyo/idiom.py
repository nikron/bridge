from bridge.services.model.idiom import ModelIdiom, IdiomError
from bridge.services.model.assets import VolumeAsset

class OnkyoIdiom(ModelIdiom):
    def create_asset(self, name, real_id, product_name):
        if real_id != "1":
            raise IdiomError("Onkyo ID's are always 1.")

        if product_name != "Receiver":
            raise IdiomError("Currently only support generic volume control.")

        return VolumeAsset(name, real_id, self.service, product_name)

    def change_state(self, asset, update):
        if 'mvl' in update:
            asset.transition('main', update['mvl'])

    def guess_asset(self, real_id, update):
        return VolumeAsset("Receiver", real_id, self.service, "Receiver"), True

    def product_names(self):
        return ["Receiver"]
