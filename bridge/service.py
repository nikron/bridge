import multiprocessing
import logging
import signal

from bridge.logging import service_configure_logging

CLOSE_MESSAGE = { 'method' : 'close', 'args' : [], 'kwargs' : {}}
DEBUG_MESSAGE = { 'method' : 'debug', 'args' : [], 'kwargs' : {}}

class BridgeService(multiprocessing.Process):
    def __init__(self, name, hub_connection, log_queue):
        multiprocessing.Process.__init__(self, name=name)
        self.hub_connection = hub_connection
        self.log_queue = log_queue

        #most services will spin on a select loop
        self.spinning = False 

        service_configure_logging(self.log_queue)

    def run(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)

    def do_remote_request(self):
        msg = self.hub_connection.recv()
        if hasattr(self, msg['method']):
            func = getattr(self, msg['method'])
            func(*msg['args'], **msg['kwargs'])

        else:
            logging.error("The method {0} is not in the object.".format(msg['method']))
            
    def close(self):
        logging.debug("Service {0}" + self.name + " is closing.")
        self.spinning = False

    def debug(self):
        logging.debug("Service " + self.name + " is debugging.")

    def remote_service_method(self, to, *args, **kwargs):
        msg = {'to' : to, 'args' : args, 'kwargs' : kwargs}

        self.hub_connection.send(msg)
