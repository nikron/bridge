import multiprocessing
import bridgelogging
import logging

CLOSE_MESSAGE = { 'method' : 'close', 'args' : [], 'kwargs' : {}}

class BridgeService(multiprocessing.Process):
    def __init__(self, name, hub_connection, log_queue):
        multiprocessing.Process.__init__(self, name=name)
        self.hub_connection = hub_connection
        self.log_queue = log_queue

        self.spinning = False #most services will spin on a select loop, but they aren't
        # right now

        bridgelogging.service_configure_logging(self.log_queue)

    def do_remote_request(self):
        try:
            msg = self.hub_connection.recv()
            self.__dict__[msg['method']](self, *msg['args'], **msg['kwargs'])

        except KeyError:
            logging.error("The method " + msg['method'] + "is not in the object.")
            
    def close(self):
        logging.debug("Service " + self.name + "is closing.")
        self.spinning = False

    def remote_service_method(self, to, *args, **kwargs):
        msg = {'from' : self.name, 'to' : to, 'args' : args, 'kwargs' : kwargs}

        self.hub_connection.send(msg)
        
