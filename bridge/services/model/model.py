"""
Model of real and virtual assets.
"""
import logging
from bridge.services.model.actions import perform_action, get_action_information, ActionError

class Model():
    """
    Model of all the connected devices and virtual information such as links.
    """
    def __init__(self):
        self.r2u = {} #real id to uuid
        self.assets = {}
        self.asset_names = []
        self.virtual_assets = [] #links will eventually be stored here

    def add_service(self, service):
        """Add an io service to the model."""
        self.r2u[service] = {}

    def get_asset(self, uuid):
        """Get asset of uuid"""
        return self.assets.get(uuid)

    def get_service_asset_uuids(self, service):
        return list(self.r2u.items())

    def get_all_asset_uuids(self):
        """Get all uuid's of all assets."""
        return list(self.assets.keys())

    def get_all_asset_names(self):
        """Get all the pretty names of the assets."""
        return self.asset_names

    def get_uuid(self, service, real_id):
        """Get the uuid corresponding to a particular service + id. """
        if service in self.r2u:
            return self.r2u[service].get(real_id)

        return None

    def add_asset(self, asset):
        """Add an asset to the model."""
        self.assets[asset.uuid] = asset

        if asset.service not in self.r2u:
            self.add_service(asset.service)

        self.r2u[asset.service][asset.get_real_id()] = asset.uuid
        self.asset_names.append(asset.name)

    def remove_asset(self, uuid):
        asset = self.get_asset(uuid)
        if not asset:
            return False

        del self.r2u[asset.service][asset.get_real_id()]
        del self.assets[asset.uuid]
        self.asset_names.remove(asset.name)

    def transform_action_to_method(self, uuid, action, *args, **kwargs):
        """Perform an action on uuid asset."""
        asset = self.assets.get(uuid)

        if asset is not None:
            return perform_action(asset, action, *args, **kwargs)
        else:
            logging.error("{0} does not exist in this model, can not perform action {1}.".format(uuid, action))
            raise KeyError

    def serializable_asset_info(self, uuid):
        """Return an asset in basic python primitives."""
        asset = self.get_asset(uuid)

        if asset:
            return asset.serializable()
        else:
            return None

    def serializable_asset_action_info(self, uuid, action):
        """Get the information of actions of an asset in base python primitives."""
        asset = self.get_asset(uuid)

        if asset:
            try:
                return get_action_information(asset, action)
            except ActionError:
                return None
        else:
            logging.error("{0} does not exist in this model, can not get action {1}.".format(type(uuid), action))
            return None
