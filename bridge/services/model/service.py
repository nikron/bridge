"""
Process to hold model and do net and io requests.
"""
import logging
from select import select

from bridge.service import BridgeService
from bridge.services.model.storage import get_storage
from bridge.services.model.idiom import IdiomError
from bridge.services.model.actions import ActionError

class ModelService(BridgeService):
    def __init__(self, io_idioms, file_name, driver_name,  hub_connection):
        super().__init__('model', hub_connection)
        self.read_list = [self.hub_connection]

        self.storage = get_storage(file_name, driver_name)
        self.model = self.storage.read_saved_model()
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
        """Summary of this service status."""
        return { 'model saved' : not self.dirty }

    def get_io_services(self):
        """List of services."""
        return list(self.io_idioms.keys())

    def get_io_service_info(self, service):
        """Seriziable info of service."""
        if service in self.io_idioms:
            return {
                    'name' : service,
                    'online' : self.io_idioms[service].online
                    }

    def get_assets(self):
        """Return a list of uuids for assets."""

        return self.model.get_all_asset_uuids()

    def create_asset(self, name, real_id, service, product_name):
        """
        Create an asset, make sure service exists  and real id doesn't already exist.
        """

        try:
            idiom = self.io_idioms[service]
        except KeyError:
            return (False, "Service `{0}` not valid.".format(service))

        try:
            asset = idiom.create_asset(name, real_id, product_name)
        except IdiomError as err:
            return (False, err.reason)

        self.model.add_asset(service, asset)
        logging.debug("Added asset {0}.".format(repr(asset)))
        self.dirty = True

        return (True, asset.uuid)

    def get_asset_info(self, uuid):
        """Get a representation of an asset in an easy to understand dict (serializable)."""
        return self.model.serializable_asset_info(uuid)

    def get_asset_action_info(self, uuid, action):
        logging.debug("Getting action info {0} from {1}.".format(action, uuid))
        return self.model.serializable_asset_action_info(uuid, action)

    def perform_asset_action(self, uuid, action, *args, **kwargs):
        """Perform an action on an asset."""
        try:
            service, targs, tkwargs = self.model.transform_action_to_method(uuid, action, *args, **kwargs)
            self.remote_async_service_method(service, *targs, **tkwargs)
        except ActionError as err:
            return err.message

        return None

    def io_update(self, service, real_id, update):
        """
        Receive an io update, use the idiom to decipher it, and request
        more information about asset if nessary.
        """

        idiom = self.io_idioms[service]
        if idiom:
            uuid = self.model.get_uuid(service, real_id)

            if uuid:
                try:
                    logging.debug("Trying to transistion to update {0}".format(update))
                    idiom.change_state(self.model.get_asset(uuid), update)

                except IdiomError:
                    logging.debug("Couldn't process update {0}.".format(update))

            else:
                logging.debug("Got an update about device {0} that we don't know about.".format(real_id))

                (asset, positive) = idiom.guess_asset(real_id, update)
                self.model.add_asset(service, asset)
                self.dirty = True

                if not positive:
                    self.remote_async_service_method(service, 'asset_info', asset.get_real_id())

        else:
            logging.error("Do not know about io service {0}.".format(service))

    def io_service_offline(self, service):
        self.io_idioms[service].online = False

    def io_service_online(self, service):
        self.io_idioms[service].online = True
