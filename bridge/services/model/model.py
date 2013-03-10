import logging

class Model():
    def __init__(self):
        self.r2u = {} #real id to uuid
        self.assets = {}
        self.links = []

    def add_service(self, service):
        self.r2u[service] = {}

    def get_uuid(self, service, real_id):
        if service in self.r2u:
            return self.r2u[service].get(real_id)

        return None

    def add_asset(self, service, asset):
        """Add an asset to the model."""
        self.assets[asset.uuid] = asset

        if service not in self.r2u:
            self.add_service(service)

        self.r2u[service][asset.real_id] = asset.uuid

        
    def net_simple(self, uuid, state):
        asset = self.assets.get(uuid)

        if asset is not None:
            asset.transition(state)
        else:
            logging.error("{0} does not exist in this model.".format(repr(uuid)))
    
    #attemps to transtiotion asset(uuid) to state
    #returns false if unsuccessful
    def io_transition(self, uuid, state):
        return self.assets[uuid].tranistion(state)

    """Hard method where we transform an arbitrary asset into another
    figure out how to do this"""
    def transform(self, uuid, asset):
        pass 
