"""
Process to hold model and do net and io requests.
"""
import logging
from select import select

from bridge.service import BridgeService
from .storage import get_storage
from bridge.services.model.idiom import IdiomError

class ModelService(BridgeService):
    def __init__(self, io_idioms, file_name, driver_name,  hub_connection, log_queue):
        super().__init__('model', hub_connection, log_queue)
        self.read_list = [self.hub_connection]

        self.storage = get_storage(file_name, driver_name)
        self.model = self.storage.read_saved_model()
        self.io_idioms = io_idioms

        for service in self.io_idioms:
            def service_function(method, *args, **kwargs):
                self.remote_async_service_method(service, method, *args, **kwargs)

            self.io_idioms[service].charge(service_function)

    def run(self):
        super().run()
        self.spinning = True

        while self.spinning:
            (read, _, _) = select(self.read_list, [], [])
            if self.hub_connection in read:
                self.read_and_do_remote_request()

    def simple_state_change(self, asset_uuid, state):
        """
        Try to do a simple state change that a non io process can do.
        """
        self.model.net_simple(asset_uuid, state)

    def get_services(self):
        return list(self.io_idioms.keys())

    def get_assets(self): 
        """Return a list of uuids for assets."""
        return self.model.get_all_asset_uuids()

    def create_asset(self, name, real_id, service, asset_class):
        """
        Creats an asset, as this method's callers is not trusted to type check,
        we have to.
        """

        try:
            idiom = self.io_idioms[service]
        except KeyError:
            return (False, "Service `{0}` not valid.".format(service))


        try:
            asset = idiom.create_asset(name, real_id, asset_class)
        except IdiomError as err:
            return (False, err.reason)

        self.model.add_asset(service, asset)
        logging.debug("Added asset {0}.".format(repr(asset)))

        return (True, asset.uuid)

    def get_asset_info(self, uuid):
        """Get a representation of an asset in easy to understand dict.""" 

        asset = self.model.get_asset(uuid)
        if asset:
            easy = {}
            easy['name'] = asset.name
            easy['uuid'] = str(asset.uuid)
            easy['real id'] = asset.get_real_id()
            easy['actions'] = list(asset.get_actions())
            easy['state'] =  asset.current_states()

            return easy
        else:
            return None

    def io_update(self, service, real_id, update):
        """
        Receive an io update, use the idiom to decipher it, and request
        more information about asset if nessary.
        """
        idiom = self.io_idioms[service]

        if idiom is not None:
            uuid = self.model.get_uuid(service, real_id)

            if uuid is not None:
                (category, state) = idiom.get_state(update)

                if not self.model.io_transition(uuid, category, state):
                    asset = idiom.guess_asset(real_id, update)

                    self.model.transform(uuid, asset)

            else:
                logging.debug("Got an update about device {0} that we don't know about.".format(real_id))

                (asset, positive) = idiom.guess_asset(real_id, update)
                self.model.add_asset(service, asset)

                if not positive:
                    self.remote_async_service_method(service, 'asset_info', asset.real_id)

        else:
            #got an update from a service we don't know about
            #probably should complain to the bridgehub about it failing
            # to do its job
            logging.error("Do not know about io service {0}.".format(service)) 

