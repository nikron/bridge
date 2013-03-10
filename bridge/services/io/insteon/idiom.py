from bridge.services.model.idiom import ModelIdiom
from bridge.services.model.assets import BlankAsset

class InsteonIdiom(ModelIdiom):
    def guess_asset(self, update):
        cmd1 = update['cmd1']
        cmd2 = update['cmd2']

        if cmd1 == b'\x03' and cmd2 == b'\x00':
            if 'ext' not in update:
                return (BlankAsset(update['id']), False)

        else:
            return (BlankAsset(update['id']), False)

    def get_state(self, update):
        pass
