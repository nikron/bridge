import logging
from select import select

from bridgeservice import BridgeService
from .model import Model
from .model_storage import get_storage

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
        self.model.simple(asset_uuid, state)
    
    #io service should call this most of the time
    def io_update(self, service, update):

        if service in self.io_idioms:
            io_idiom = self.io_idioms[io_idiom]

            self.model.io_update(io_idiom, update)
        
        else:
            #got an update from a service we don't know about
            #probably should complain to the bridgehub about it failing
            # to do its job
            logging.error("Do not know about io service {0}.".format(service)) 

