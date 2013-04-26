"""
Process to hold model and do net and io requests.
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
    :type hub_connection: Pipe
    """

    def __init__(self, io_idioms, directory, hub_connection):
        super().__init__('model', hub_connection)
        self.read_list = [self.hub_connection]

        self.storage = ModelStorage(directory)
        self.model = self.storage.read_model(io_idioms)
        self.io_idioms = io_idioms
        self.dirty = False

    def run(self):
        self.mask_signals()
        self.spinning = True

        while self.spinning:
            (read, _, _) = select(self.read_list, [], [])
            if self.hub_connection in read:
                self.read_and_do_remote_request()

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

    def save(self, file_name=None):
        try:
            ret = self.storage.write_model(self.model, file_name)
            return ret, ''

        except AttributeError as ex:
            return False, ex.args[0]

    def get_io_services(self):
        """List of services."""
        return list(self.io_idioms.keys())

    def get_io_service_info(self, service):
        """Seriziable info of service."""
        if service in self.io_idioms:
            return {
                    'name' : service,
                    'online' : self.io_idioms[service].online,
                    'assets' : self.model.get_service_asset_uuids(service)
                    }

    def get_assets(self):
        """Return a list of uuids for assets."""

        return self.model.get_all_asset_uuids()

    def create_asset(self, name, real_id, service, product_name):
        """
        Create an asset, make sure service exists  and real id doesn't already exist.
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
        return self.model.remove_asset(uuid)

    def get_asset_info(self, uuid):
        """Get a representation of an asset in an easy to understand dict (serializable)."""
        return self.model.serializable_asset_info(uuid)

    def get_asset_action_info(self, uuid, action):
        logging.debug("Getting action info {0} from {1}.".format(action, uuid))
        return self.model.serializable_asset_action_info(uuid, action)

    def set_asset_name(self, uuid, name):
        self.model.set_asset_name(uuid, name)

    def perform_asset_action(self, uuid, action, *args, **kwargs):
        """Perform an action on an asset."""
        try:
            msg = self.model.transform_action_to_message(uuid, action, *args, **kwargs)
            if msg:
                self.hub_connection.send(msg)
            else:
                return "Asset not found."
        except ActionError as err:
            return err.message

        return None

    def control_asset(self, uuid, category, state):
        msg = self.model.get_asset_control_message(uuid, category, state)
        self.hub_connection.send(msg)

    def io_update(self, service, real_id, update):
        """
        Receive an io update, use the idiom to decipher it, and request
        more information about asset if nessary.
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

    def io_service_offline(self, service):
        self.io_idioms[service].online = False

    def io_service_online(self, service):
        self.io_idioms[service].online = True

    def _add_asset(self, service, asset, positive):
        logging.debug("Adding asset {0}.".format(str(asset)))
        self.model.add_asset(asset)
        self.dirty = True

        self.remote_async_service_method(service, 'asset_status', asset.get_real_id())

        if not positive:
            self.remote_async_service_method(service, 'asset_info', asset.get_real_id())
