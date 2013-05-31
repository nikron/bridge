from bridge.services.model.idiom import ModelIdiom, IdiomError
from bridge.model.assets.onkyo_assets import OnkyoTXNR609

class OnkyoIdiom(ModelIdiom):
    def create_asset(self, name, real_id, product_name):
        if product_name != "Onkyo TX-NR609":
            raise IdiomError("Currently only support generic volume control.")

        return OnkyoTXNR609(name, real_id, self.service, product_name)

    def change_state(self, asset, update):
        """
        The eisp driver is not general, it just sends update tuples
        in a way that translates into a transition.
        """
        asset.transition(*update)

    def guess_asset(self, real_id, update):
        return OnkyoTXNR609("Receiver", real_id, self.service, "Onkyo TX-NR609"), True

    def product_names(self):
        return ["Onkyo TX-NR609"]
