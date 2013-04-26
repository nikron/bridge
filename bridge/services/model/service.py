"""
Service that keeps track of the device status and controls them.
"""
import logging
from select import select

from bridge.service import BridgeService
from bridge.services.model.storage import ModelStorage
from bridge.services.model.idiom import IdiomError
from bridge.services.model.actions import ActionError

class ModelService(BridgeService):
    """
    Read events from most bridge services to manipulate and display assets/devices.

    :param io_idioms: A dictionary of a IO service name to an idiom on how to use it.
    :type io_idioms: dict

    :param directory: Directory to store model information.
    :type directory: str

    :param hub_connection: Connection to talk to BridgeHub.
    :type hub_connection: :class:`Pipe`
    """

    def __init__(self, io_idioms, directory, hub_connection):
        super().__init__('model', hub_connection)
        self.read_list = [self.hub_connection]

        self.storage = ModelStorage(directory)
        self.model = self.storage.read_model(io_idioms)
        self.io_idioms = io_idioms
        self.dirty = False

    def control_asset(self, uuid, category, state):
        """
        Control an asset by getting its control :class:`BridgeMessage`, and the send it.

        :param uuid: The UUID of an asset.
        :type uuid: uuid

        :param category:  The category of the state to control the asset to.
        :type category: str

        :param state: The state of the state to control the asset to.
        :type state: str
        """
        msg = self.model.get_asset_control_message(uuid, category, state)
        self.hub_connection.send(msg)

    def create_asset(self, name, real_id, service, product_name):
        """
        Create an asset, make sure service exists  and real id doesn't already exist.
        This method is meant to be called from a front end, like the http front end.
        Therefore it does some bounds checking, and returns a string the a client
        could display.

        :param name: Name of he asset to create.
        :type name: str

        :param real_id: Real id identifying the asset to the IO service
        :type real_id: str

        :param service: The service to attach the asset to.
        :type service: str

        :param product_name: The string that the idiom will use to to create an appropriate asset.
        :type product_name: str

        :return: Return a tuple of whether the creation succeeded, an asset uuid if it succeded, and
        an error reason if it did not.
        :rtype: (bool, str)
        """
        if service not in self.io_idioms :
            return False, "Service `{0}` not valid.".format(service)

        if self.model.get_asset_uuid(service, real_id):
            return False, "Already have an asset on that id."

        try:
            asset = self.io_idioms[service].create_asset(name, real_id, product_name)
            self._add_asset(service, asset, True)

            return True, asset.uuid

        except IdiomError as err:
            return False, err.reason

    def delete_asset(self, uuid):
        """
        Delete an asset.

        :param uuid: UUID of asset to delete.
        :type uuid: uuid

        :return: Whether deletion succeeded.
        :type: bool
        """
        return self.model.remove_asset(uuid)

    def get_assets(self):
        """
        :return: List of all :class:`Asset`s in UUID form.
        :type: [uuid]
        """
        return self.model.get_all_asset_uuids()

    def get_asset_action_info(self, uuid, action):
        """
        Get action info about an asset.

        :param uuid: UUID of the asset.
        :type uuid: uuid

        :param action: Name of the action.
        :type action: str

        :return: Se realizable form of an asset.
        :rtype: dict
        """
        logging.debug("Getting action info {0} from {1}.".format(action, uuid))
        return self.model.serializable_asset_action_info(uuid, action)

    def get_asset_info(self, uuid):
        """
        Get a representation of an asset in an easy to understand dict (serializable).

        :param uuid: The UUID of an asset.
        :type uuid: uuid

        :return: Asset information in serializable form.
        :rtype: dict
        """
        return self.model.serializable_asset_info(uuid)

    def set_asset_name(self, uuid, name):
        """
        Set the name of an asset.

        :param uuid: The UUID of an asset.
        :type uuid: uuid

        :param name: Thew new name of an asset.
        :type name: str
        """
        self.model.set_asset_name(uuid, name)

    def get_info(self):
        """
        Summary of this service status.

        :return: A dict of model status, currently only information saved state.
        :rtype: dict
        """
        ser = {
                'model dirty' : self.dirty ,
                'model current save file' : self.storage.get_current_file(),
                'model save files' : self.storage.get_files()
                }

        return ser

    def get_io_services(self):
        """
        List of services.

        :return: List of IO services the idiom knows about.
        :rtype: [str]
        """
        return list(self.io_idioms.keys())

    def get_io_service_info(self, service):
        """
        Seriziable info of service.

        :param service: The service to get information about.
        :type service: str

        :return: Information of an IO service in python primitives.
        :rtype: dict
        """
        if service in self.io_idioms:
            return {
                    'name' : service, 'online' : self.io_idioms[service].online,
                    'assets' : self.model.get_service_asset_uuids(service)
                    }

    def perform_asset_action(self, uuid, action, *args, **kwargs):
        """
        Perform an action on an asset.
        """
        try:
            msg = self.model.transform_action_to_message(uuid, action, *args, **kwargs)
            if msg:
                self.hub_connection.send(msg)
            else:
                return "Asset not found."
        except ActionError as err:
            return err.message

        return None

    def io_service_offline(self, service):
        """
        Tell the model an IO service is offline.

        :param service:
        :type service: str
        """
        self.io_idioms[service].online = False

    def io_service_online(self, service):
        """
        Tell the model an IO service is online.

        :param service:
        :type service: str
        """
        self.io_idioms[service].online = True

    def io_update(self, service, real_id, update):
        """
        The method an IO service should call when it gets an update.
        Attempts to transition the asset of the real_id using the idiom associated
        with IO service, but if the model does not have an asset associated with the
        real_id then it attempts to create that asset.

        :param service: The service calling this method.
        :type service: str

        :param real_id: The real id used by the service and its idiom.
        :type real_id: object

        :param update: The update sent from an IO service.
        :type update: object
        """
        idiom = self.io_idioms[service]
        if idiom:
            uuid = self.model.get_asset_uuid(service, real_id)

            if uuid:
                try:
                    logging.debug("Trying to transistion to update {0}".format(update))
                    idiom.change_state(self.model.get_asset(uuid), update)

                except IdiomError:
                    logging.debug("Couldn't process update {0}.".format(update))

            else:
                logging.debug("Got an update about device {0} that we don't know about.".format(real_id))

                asset, positive = idiom.guess_asset(real_id, update)
                self._add_asset(service, asset, positive)

        else:
            logging.error("Do not know about io service {0}.".format(service))

    def run(self):
        self.mask_signals()
        self.spinning = True

        while self.spinning:
            (read, _, _) = select(self.read_list, [], [])
            if self.hub_connection in read:
                self.read_and_do_remote_request()

    def save(self, file_name=None):
        """
        Save the model to a file name.

        :param file_name: Name of a file to save the model to
        :type str:

        :return: Outward facing method, returns a tuple of success, message
        :rtype: (bool, str)
        """
        try:
            ret = self.storage.write_model(self.model, file_name)
            return ret, ''

        except AttributeError as ex:
            return False, ex.args[0]

    def _add_asset(self, service, asset, positive):
        """
        Add an initialized asset, note that the saved model configuration is no longer correct, and
        request more information from the IO service.

        :param service:
        :type service: str

        :param asset:
        :type asset: :class:`Asset`

        :param positive: If the asset is positively correct.
        :type positive: bool
        """
        logging.debug("Adding asset {0}.".format(str(asset)))
        self.model.add_asset(asset)
        self.dirty = True

        self.remote_async_service_method(service, 'asset_status', asset.get_real_id())

        if not positive:
            self.remote_async_service_method(service, 'asset_info', asset.get_real_id())
