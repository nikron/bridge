from bridge.model.idiom import ModelIdiom

class InsteonIdiom(ModelIdiom):
    def guess_asset(self, update):
        #well we can do stuff on this one
        if update['command'] == 'production description':
            pass
           
        else:
            return (None, False)
