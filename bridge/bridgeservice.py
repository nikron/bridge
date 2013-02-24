import multiprocessing
import bridgelogging
import logging

class BridgeService(multiprocessing.Process):
    def __init__(self, name, hub_connection, log_queue):
        multiprocessing.Process.__init__(self, name=name)
        self.hub_connection = hub_connection
        self.log_queue = log_queue
        self.callbacks = {}

        bridgelogging.service_configure_logging(self.log_queue)

    def run(self):
        self.main()

    def register_callback(self, action, callback):
        self.callbacks[action] = callback

    def do_callback(self):
        try:
            msg = self.hub_connection.recv()
            self.callbacks[msg['action']](self, msg)

        except KeyError:
            logging.error("The key " + msg['action'] + "is located in callbacks.")
            
