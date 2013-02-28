import logging
from select import select

from bridgeservice import BridgeService

#An ioservice should be passed an interface, something that you can
#call select on
class IOService(BridgeService):
    def __init__(self, name, interface, hub_connection, log_queue):
        super().__init__(name, hub_connection, log_queue)
        self.interface = interface

        self.read_list = [self.hub_connection]

        if interface is not None:
            self.read_list.append(interface)

    def run(self):
        super().run()
        self.spinning = True

        while self.spinning:
            (read, write, exception) = select(self.read_list, [], [])
            if self.hub_connection in read:
                self.do_remote_request()
            if self.interface in read:
                self.read_interface()

    def update_model(self, update):
        self.remote_service_method('model', 'update', update)

    def read_interface(self):
        raise NotImplementedError
