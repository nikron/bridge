"""
Base class of services of bridge, automatically hooks up logging, and
sets up methods to messages easier.
"""
import multiprocessing
import logging
import signal

from bridge.logging_service import service_configure_logging

CLOSE_MESSAGE = { 'method' : 'close', 'args' : [], 'kwargs' : {}}
DEBUG_MESSAGE = { 'method' : 'debug', 'args' : [], 'kwargs' : {}}

class BridgeService(multiprocessing.Process):
    """Base class of bridge services, needs a connection to hub and log."""
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
        """
        Intended for subclasses to call when they have time communicate with
        rest of the program.  Automatically calls a function on self.
        """
        msg = self.hub_connection.recv()
        if hasattr(self, msg['method']):
            func = getattr(self, msg['method'])
            func(*msg['args'], **msg['kwargs'])

        else:
            logging.error("The method {0} is not in the object.".format(msg['method']))

    def close(self):
        logging.debug("Service {0} is closing.".format(self.name))
        self.spinning = False

    def debug(self):
        logging.debug("Service {0} is debugging.".format(self.name))

    def remote_service_method(self, to, *args, **kwargs):
        msg = {'to' : to, 'args' : args, 'kwargs' : kwargs}

        self.hub_connection.send(msg)
