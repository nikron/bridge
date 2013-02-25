import multiprocessing
import bridgelogging
import logging

CLOSE_MESSAGE = { 'method' : 'close' }

class BridgeService(multiprocessing.Process):
    def __init__(self, name, hub_connection, log_queue):
        multiprocessing.Process.__init__(self, name=name)
        self.hub_connection = hub_connection
        self.log_queue = log_queue

        self.spinning = False #most services will spin on a select loop, but they aren't
        # right now

        bridgelogging.service_configure_logging(self.log_queue)

    def do_callback(self):
        try:
            msg = self.hub_connection.recv()
            self.__dict__[msg['method']](self, msg)

        except KeyError:
            logging.error("The method " + msg['method'] + "is not in the object.")
            
    def close(self, msg):
        self.spinning = False
