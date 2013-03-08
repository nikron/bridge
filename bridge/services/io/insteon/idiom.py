from bridge.services.model.idiom import ModelIdiom
from bridge.services.model.assets import BlankAsset

class InsteonIdiom(ModelIdiom):
    def guess_asset(self, update):
        #well we can do stuff on this one
        if update['command'] == 'production description':
            pass

        else:
            return (BlankAsset(update['id']), False)

    def get_state(self, update):
        pass
