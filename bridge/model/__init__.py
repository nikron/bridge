"""
Model of real and virtual assets.  Mostly just keeps them in a series of dictionaries,
so that they can be refered to and accessed in easy ways.
"""

import logging
from bridge.model.actions import perform_action, get_action_information, ActionError

class Model():
    """
    Model of all the connected devices and virtual information such as links.
    Does not actively change assets, expects outsiders to use this class to store assets,
    and change them.  This class will become more important with virtual assets, however right now
    it barely does anything.
    """

    def __init__(self):
        self.r2u = {} #real id to uuid
        self.assets = {}
        self.virtual_assets = [] #links will eventually be stored here

    def add_asset(self, asset):
        """
        Add an asset to the model.

        :param asset: Intialized asset to add to the model.
        :type asset: :class:`Asset`
        """
        self.assets[asset.uuid] = asset
        service = asset.get_service()

        if service not in self.r2u:
            self.add_service(service)

        self.r2u[service][asset.get_real_id()] = asset.uuid

    def add_service(self, service):
        """
        Add an io service to the model.

        :param service: The name of the service.
        :type service: str
        """
        self.r2u[service] = {}

    def get_all_asset_uuids(self):
        """
        Get the UUID of all the assets associated with the model.

        :return: A list of uuids.
        :rtype: [uuid]
        """
        return list(self.assets.keys())

    def get_asset(self, uuid):
        """
        Get an asset by using its UUID, fastest and canonical way of accessing assets.

        :param uuid: The universal identifier of an asset.
        :type uuid: uuid

        :return:  An asset or None if it is not found.
        :rtype: :class:`Asset`
        """
        return self.assets.get(uuid)

    def get_asset_control_message(self, uuid, category, state):
        """
        Get the control :class:`BridgeMessage` associated with controling an asset to
        transition to a particular state.

        :param uuid: UUID of an asset.
        :type uuid: uuid

        :param category: The category to get the control object.
        :type category: str

        :param state: The state that the object controls.
        :type state: str

        :return: The :class:`BridgeMessage`  associated with changing to a state.
        :rtype: :class:`BridgeMessage`
        """
        return self.get_asset(uuid).get_control_message(category, state)

    def get_asset_uuid(self, service, real_id):
        """
        Get the UUID corresponding to a particular service + id.

        :param service: Name of the service
        :type service: str

        :param real_id: Identfier used by the service.
        :type real_id: object

        :return: The identifier that a client should refer to this asset as.
        :rtype: uuid
        """
        if service in self.r2u:
            return self.r2u[service].get(real_id)

        return None

    def get_service_asset_uuids(self, service):
        """
        Get all assets associated with a service.

        :param service: The name of the service.
        :type service: str:

        :return: A list of assets.
        :rtype: [uuid]
        """
        if service in self.r2u:
            return list(self.r2u[service].items())
        else:
            return []

    def remove_asset(self, uuid):
        """
        Remove an asset.

        :param uuid: The UUID of the asset to remove.
        :type uuid: uuid

        :return: If the operation was successful.
        :rtype: bool
        """
        asset = self.get_asset(uuid)
        if not asset:
            return False

        del self.r2u[asset.service][asset.get_real_id()]
        del self.assets[asset.uuid]

        return True

    def serializable_asset_action_info(self, uuid, action):
        """
        Get the information of actions of an asset in base python primitives.
        Inforamtion mean to display to an asset about actions of an asset.

        :param uuid: The asset of the action.
        :type uuid: uuid

        :param action:
        :type action:

        :return: A serializable form of an asset, and None if there is an error.
        :rtype: dict
        """
        asset = self.get_asset(uuid)

        if asset:
            try:
                return get_action_information(asset, action)
            except ActionError:
                return None
        else:
            logging.error("{0} does not exist in this model, can not get action {1}.".format(type(uuid), action))
            return None

    def serializable_asset_info(self, uuid):
        """
        Return an asset in basic python primitives.

        :param uuid: The asset to get info about.
        :type uuid: uuid

        :return: The asset in serializable form.
        :rtype: dict
        """
        asset = self.get_asset(uuid)

        if asset:
            return asset.serializable()
        else:
            return None

    def set_asset_name(self, uuid, name):
        """
        Convenience method to set an asset name.

        :param uuid: The UUID of an asset.
        :type uuid: uuid

        :param name: New name for the asset.
        :type name: str
        """
        asset = self.get_asset(uuid)
        asset.name = name

    def transform_action_to_message(self, uuid, action, *args, **kwargs):
        """
        Perform an action on UUID asset.
        An action must return a BridgeMessge, so this gets that and returns it.

        :param uuid: The asset to perform the action on.
        :type uuid: uuid

        :param action: The action to perform.
        :type action: str

        :param *args: The arguments for the action.
        :type args: list

        :param kwargs: The keyword arguments for the action.
        :type kwargs: dict

        :return: :class:`BridgeMessage` if successful or None if unsuccessful
        :rtype: :class:`BridgeMessage`
        """
        asset = self.assets.get(uuid)

        if asset is not None:
            return perform_action(asset, action, *args, **kwargs)
        else:
            logging.error("{0} does not exist in this model, can not perform action {1}.".format(uuid, action))
            return None
