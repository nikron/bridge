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

    #the network frontend uses this to do most of its work
    def simple_state_change(self, asset_uuid, state):
        self.model.net_simple(asset_uuid, state)

    #io service should call this most of the time
    def io_update(self, service, update):
        idiom = self.io_idioms[service]

        if idiom is not None:
            uuid = self.model.get_uuid(service, update['id'])

            if uuid is not None:
                state = idiom.get_state(update)

                if not self.model.io_transistion(uuid, state):
                    asset = idiom.guess_asset(update)

                    self.model.transform(uuid, asset)

            else:
                logging.debug("Got an update about device {0} that we don't know about.".format(
                    update['id']))

                asset = idiom.guess_asset(service, update)
                self.model.add_asset(asset)

        else:
            #got an update from a service we don't know about
            #probably should complain to the bridgehub about it failing
            # to do its job
            logging.error("Do not know about io service {0}.".format(service)) 

