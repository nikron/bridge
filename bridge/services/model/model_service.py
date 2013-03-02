import logging
from select import select

from bridgeservice import BridgeService
from .model import Model

class ModelService(BridgeService):
    def __init__(self, io_services, driver_name,  hub_connection, log_queue):
        super().__init__('model', hub_connection, log_queue)
        self.read_list = [self.hub_connection]

        #self.storage = config.storage_driver()
        #self.model = self.storage.read_saved_model()

    def run(self):
        super().run()
        self.spinning = True

        while self.spinning:
            (read, write, exception) = select(self.read_list, [], [])
            if self.hub_connection in read:
                self.do_remote_request()

    def simple_state_change(self, asset_uuid, state):
        self.model.simple(asset_uuid, state)
        
    def io_update(self, service, update):
        real_id = update['id']
        asset = model.r2u[service][real_id]
        
        #sanity check
        if asset.service.uuid == service:
            asset.update(update)
