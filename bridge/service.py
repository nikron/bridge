"""
Base class of services of bridge, automatically hooks up logging, and
sets up methods to messages easier.
"""
import multiprocessing
import logging
import signal
from collections import namedtuple

BridgeMessage = namedtuple('BridgeMessage', ['to', 'method', 'args', 'kwargs'])

from bridge.logging_service import service_configure_logging

CLOSE_MESSAGE = BridgeMessage(None, 'close', [], {})
DEBUG_MESSAGE = BridgeMessage(None, 'debug', [], {})

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
        if hasattr(self, msg.method):
            func = getattr(self, msg.method)
            func(*msg.args, **msg.kwargs)

        else:
            logging.error("The method {0} is not in the object.".format(msg.method))

    def close(self):
        """Attempt to close the this service if it spinning."""
        logging.debug("Service {0} is closing.".format(self.name))
        self.spinning = False

    def debug(self):
        """Spit something to log."""
        logging.debug("Service {0} is debugging.".format(self.name))

    def remote_service_method(self, service, method, *args, **kwargs):
        """Call a method on a remote service."""
        msg = BridgeMessage(service, method, args, kwargs)

        self.hub_connection.send(msg)
