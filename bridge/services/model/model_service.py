import logging
from select import select

from bridgeservice import BridgeService

class ModelService(BridgeService):
    def __init__(self, configuration, hub_connection, log_queue):
        super().__init__('model', hub_connection, log_queue)
        self.read_list = [self.hub_connection]

    def run(self):
        super().run()
        while self.spinning:
            (read, write, exception) = select(self.read_list, [], [])
            if self.hub_connection in read:
                self.do_remote_request()


#    def scan_network(self):
