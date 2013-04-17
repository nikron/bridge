"""
Base class of services of bridge, automatically hooks up logging, and
sets up methods to messages easier.
"""
from  multiprocessing import Process

import logging
import signal

class BridgeMessage():
    ASYNC = 'async'
    BLOCKING = 'blocking'
    REPLY = 'reply'
    CLOSE = 'close'

    def __init__(self, to, _type, method, args, kwargs, ret):
        self.to = to
        self.type = _type
        self.method = method
        self.args = args
        self.kwargs = kwargs
        self.ret = ret

    @classmethod
    def create_async(cls, to, method, *args, **kwargs):
        return cls(to, cls.ASYNC, method, args, kwargs, None)

    @classmethod
    def create_block(cls, to, _from, method, *args, **kwargs):
        return cls(to, cls.BLOCKING, method, args, kwargs, _from)

    @classmethod
    def create_reply(cls, block_message, ret):
        return cls(block_message.ret, cls.REPLY, None, None, None, ret)


CLOSE_MESSAGE = BridgeMessage(None, BridgeMessage.CLOSE, None, None, None, None)

class BridgeService(Process):
    """Base class of bridge services, needs a connection to hub."""
    def __init__(self, name, hub_connection):
        Process.__init__(self, name=name)
        self.hub_connection = hub_connection

        #most services will spin on a select loop
        self.spinning = False

        #while blocking, need to keep track of mesages
        self.blocked_messages = []

    def mask_signals(self):
        """Mask signals (nameley keyboard interrupts)"""
        signal.signal(signal.SIGINT, signal.SIG_IGN)

    def read_and_do_remote_request(self):
        """Receive object from connection, and do it assuming tis a BridgeMessage."""
        msg = self.hub_connection.recv()
        self.do_remote_request(msg)

    def do_remote_request(self, msg):
        """
        Intended for subclasses to call when they have time communicate with
        rest of the program.  Automatically calls a function on self.
        """

        if msg.type == BridgeMessage.CLOSE:
            self.close()

        elif hasattr(self, msg.method):
            func = getattr(self, msg.method)
            ret = func(*msg.args, **msg.kwargs)

            if msg.type == BridgeMessage.BLOCKING:
                reply = BridgeMessage.create_reply(msg, ret)
                self.hub_connection.send(reply)

        else:
            logging.error("The method {0} is not in the object.".format(msg.method))

    def close(self):
        """Attempt to close the this service if it spinning."""

        logging.debug("Service {0} is closing.".format(self.name))
        self.spinning = False

    def remote_async_service_method(self, service, method, *args, **kwargs):
        """Call a method on a remote service."""

        msg = BridgeMessage.create_async(service, method, *args, **kwargs)
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
        msg = BridgeMessage.create_block(service, self.name, method, *args, **kwargs)
        self.hub_connection.send(msg)

        self.spinning = True
        while self.spinning:
            msg = self.hub_connection.recv()
            if msg.type == BridgeMessage.CLOSE:
                self.close()
            elif msg.type == BridgeMessage.REPLY:
                return msg.ret
            else:
                self.blocked_messages.append(msg)
