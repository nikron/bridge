"""
Base class for each service of Bridge.
"""
from  multiprocessing import Process

import logging
import signal

class BridgeMessage():
    """
    Object that services use to marshall remote calls between each other.

    :param to: Service the object is intended for.
    :type to: str

    :param _type: Type of message: must be one of the constants.
    :type _type: str

    :param method: Method to call on the remote service.
    :type method: str

    :param args: List of regular arguments for the remote method.
    :type args: list

    :param kwargs: Keyword arguments for the rmote method.
    :type kwargs: dict

    :param ret: For use by BridgeService, facilitates blocking methods.
    :type ret: object
    """

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
        """
        Create a message that will be asynchronisally passed to the remote service.

        :param to: Service the object is intended for.
        :type to: str

        :param method: Method to call on the remote service.
        :type method: str

        :param args: List of regular arguments for the remote method.
        :type args: list

        :param kwargs: Keyword arguments for the rmote method.
        :type kwargs: dict

        :return: A message to be sent.
        :rtype: BridgeMessage
        """

        return cls(to, cls.ASYNC, method, args, kwargs, None)

    @classmethod
    def create_block(cls, to, _from, method, *args, **kwargs):
        """
        Create a message that will block the service until a reply is sent.

        :param to: Service the object is intended for.
        :type to: str

        :param _from: The service the reply will be sent to.
        :type _from: str

        :param method: Method to call on the remote service.
        :type method: str

        :param args: List of regular arguments for the remote method.
        :type args: list

        :param kwargs: Keyword arguments for the rmote method.
        :type kwargs: dict

        :return: A message to be sent.
        :rtype: BridgeMessage
        """

        return cls(to, cls.BLOCKING, method, args, kwargs, _from)

    @classmethod
    def create_reply(cls, block_message, ret):
        """
        Create a message for internal use for blocking message calls.

        :param block_message: The message that was sent to this service.
        :type block_message: BridgeMessage

        :return: A reply message to be sent.
        :rtype: BridgeMessage
        """
        return cls(block_message.ret, cls.REPLY, None, None, None, ret)


CLOSE_MESSAGE = BridgeMessage(None, BridgeMessage.CLOSE, None, None, None, None)

class BridgeService(Process):
    """
    Base class of bridge services.
    Is a Process, from multiprocessing.

    :param name: Name of the service, used for remote service calls.
    :type name: str

    :param hub_connection: Connection to the hub to pass messages to and from.
    :type hub_connection: Pipe
    """
    def __init__(self, name, hub_connection):
        Process.__init__(self, name=name)
        self.hub_connection = hub_connection

        #most services will spin on a select loop
        self.spinning = False

        #while blocking, need to keep track of mesages
        self.blocked_messages = []

    def clear_blocked_requests(self):
        """
        Method to clear blocked calls; only to call if you making blocking calls.
        """
        for blocked in self.blocked_messages:
            self.do_remote_request(blocked)

    def close(self):
        """
        Attempt to close the this service if it spinning.
        """
        logging.debug("Service {0} is closing.".format(self.name))
        self.spinning = False

    def do_remote_request(self, msg):
        """
        Subclasses can automatically handle BridgeMessages using this method.
        Finds and calls local method using the passed message.

        :param msg: Message from another service.
        :type msg: BridgeMessage
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

    @staticmethod
    def mask_signals():
        """
        Mask keyboard interrupts to the current process.
        """
        signal.signal(signal.SIGINT, signal.SIG_IGN)

    def read_and_do_remote_request(self):
        """
        For subclasses to read and execute a the object comming from the BridgeHub, assumes it is a
        Bridgemessage.
        """
        msg = self.hub_connection.recv()
        self.do_remote_request(msg)

    def remote_async_service_method(self, service, method, *args, **kwargs):
        """
        Call a method on a remote service.

        :param service: Remote service.
        :type service: str

        :param method: Method to call.
        :type method: str

        :param args: Arguments for remote method.
        :type args: list

        :param args: Keyword arguments for remote method.
        :type args: dict
        """
        msg = BridgeMessage.create_async(service, method, *args, **kwargs)
        self.hub_connection.send(msg)

    def remote_block_service_method(self, service, method, *args, **kwargs):
        """
        Call a method on a remote service in a blocking fashion in order to
        get a reply. Never use this method.

        :param service: Remote service.
        :type service: str

        :param method: Method to call.
        :type method: str

        :param args: Arguments for remote method.
        :type args: list

        :param args: Keyword arguments for remote method.
        :type args: dict

        :return: Return of remote method.
        :rtype: object
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
