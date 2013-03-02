import logging

class Model():
    def __init__(self, default_configuration=True):
        self.r2u = {} #real id to uuid
        self.u2r = {} #uuid to real
        self.assets = {}
        self.links = []

    def simple(self, uuid, state):
        try:
            asset = self.assets[uuid]
            asset.transition(state)

        except KeyError:
            logging.error("UUID " + repr(uuid) + " does not exist in this model.")
    #def update_from_io(self, update):
