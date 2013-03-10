"""
Process to hold model and do net and io requests.
"""
import logging
from select import select

from bridge.service import BridgeService
from .storage import get_storage

class ModelService(BridgeService):
    def __init__(self, io_idioms, file_name, driver_name,  hub_connection, log_queue):
        super().__init__('model', hub_connection, log_queue)
        self.read_list = [self.hub_connection]

        self.storage = get_storage(file_name, driver_name)
        self.model = self.storage.read_saved_model()
        self.io_idioms = io_idioms

    def run(self):
        super().run()
        self.spinning = True

        while self.spinning:
            (read, write, exception) = select(self.read_list, [], [])
            if self.hub_connection in read:
                self.do_remote_request()

    def simple_state_change(self, asset_uuid, state):
        """
        Try to do a simple state change that a non io process can do.
        """
        self.model.net_simple(asset_uuid, state)

    def io_update(self, service, real_id, update):
        """
        Receive an io update, use the idiom to decipher it, and request
        more information about asset if nessary.
        """
        idiom = self.io_idioms[service]

        if idiom is not None:
            uuid = self.model.get_uuid(service, real_id)

            if uuid is not None:
                state = idiom.get_state(update)

                if not self.model.io_transition(uuid, state):
                    asset = idiom.guess_asset(real_id, update)

                    self.model.transform(uuid, asset)

            else:
                logging.debug("Got an update about device {0} that we don't know about.".format(real_id))

                (asset, positive) = idiom.guess_asset(real_id, update)
                self.model.add_asset(service, asset)

                if not positive:
                    self.remote_service_method(service, 'asset_info', asset.real_id)

        else:
            #got an update from a service we don't know about
            #probably should complain to the bridgehub about it failing
            # to do its job
            logging.error("Do not know about io service {0}.".format(service)) 

