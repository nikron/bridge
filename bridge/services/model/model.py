class AssetModel():
    def __init__(self, default_configuration=True):
        self.r2u = {} #real id to uuid
        self.u2r = {} #uuid to real
        self.assets = []

    #def update_from_io(self, update):

