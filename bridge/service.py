"""
Base class of services of bridge, automatically hooks up logging, and
sets up methods to messages easier.
"""
from  multiprocessing import Process

import logging
import signal
from collections import namedtuple

BridgeMessage = namedtuple('BridgeMessage', ['to', 'type', 'method', 'args', 'kwargs', 'ret'])

from bridge.logging_service import service_configure_logging

CLOSE_MESSAGE = BridgeMessage(None, 'close', None, None, None, None)

class BridgeService(Process):
    """Base class of bridge services, needs a connection to hub and log."""
    def __init__(self, name, hub_connection, log_queue):
        Process.__init__(self, name=name)
        self.hub_connection = hub_connection
        self.log_queue = log_queue

        #most services will spin on a select loop
        self.spinning = False

        service_configure_logging(self.log_queue)

        #while blocking, need to keep track of mesages
        self.blocked_messages = []

    def run(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)

    def read_and_do_remote_request(self):
        msg = self.hub_connection.recv()
        self.do_remote_request(msg)

    def do_remote_request(self, msg):
        """
        Intended for subclasses to call when they have time communicate with
        rest of the program.  Automatically calls a function on self.
        """

        if msg.type == 'close':
            self.close()

        elif hasattr(self, msg.method):
            func = getattr(self, msg.method)
            ret = func(*msg.args, **msg.kwargs)

            if msg.type == 'block':
                reply = BridgeMessage(msg.ret, 'reply', None, None, None, ret)
                self.hub_connection.send(reply)

        else:
            logging.error("The method {0} is not in the object.".format(msg.method))

    def close(self):
        """Attempt to close the this service if it spinning."""

        logging.debug("Service {0} is closing.".format(self.name))
        self.spinning = False

    def remote_async_service_method(self, service, method, *args, **kwargs):
        """Call a method on a remote service."""

        msg = BridgeMessage(service, 'async', method, args, kwargs)
        self.hub_connection.send(msg)

    def clear_blocked_requests(self):
        """Method to clear blocked calls; only to call if you making blocking calls."""

        for blocked in self.blocked_messages:
            self.do_remote_request(blocked)

    def remote_block_service_method(self, service, method, *args, **kwargs):
        """
        Send a blocking call on a service, never use this method easily results in
        deadlocks.
        """

        msg = BridgeMessage(service, 'block', method, args, kwargs)
        self.hub_connection.send(msg)

        while self.spinning:
            msg = self.hub_connection.recv()
            if msg.type == 'close':
                self.close()
            elif msg.type == 'reply':
                return msg.ret
            else:
                self.blocked_messages.append(msg)
