import logging

class Model():
    def __init__(self):
        self.r2u = {} #real id to uuid
        self.u2r = {} #uuid to real
        self.assets = {}
        self.links = []

    def simple(self, uuid, state):
        try:
            asset = self.assets[uuid]
            asset.transition(state)

        except KeyError:
            logging.error("{0} does not exist in this model.".format(repr(uuid)))

    def io_update(self, idiom, update):
        real_id = update['id']

        if real_id in self.model.r2u[idiom.name]:
            asset = self.model.r2u[idiom.name][real_id]

            #sanity check
            #maybe we shouldn't even check
            if asset.service.uuid == service:
                asset.update(update)
            else:
                logging.error("An asset isn't mapped to its uuid?!") 
    
        else:
            #okay we got an update for a device we don't know about
            #lets create an asset

            self.create_asset_from_guesswork(service, update)

    def create_asset_from_guesswork(self, idiom, update):
        (asset, positive) = idiom.guess_asset(update)

        if not positive:
            idiom.request_more_information(asset)
