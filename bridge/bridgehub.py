import multiprocessing
import bridgelogging
from service.insteon.insteonservice import InsteonIMService
import service.insteon.insteonservice
from select import select

class BridgeHub():
    def __init__(self, configuration, *args, **kwargs):
        self.logging_service = bridgelogging.LoggingService()
        self.connections = []
        self.services = {}

    def run(self):
        #start the logging process immediately
        self.logging_service.start()
        bridgelogging.service_configure_logging(self.logging_service.queue)
        
        #start each service
        for service in [InsteonIMService]:
            #create a pipe then store our end and the process
            (ours, its) = multiprocessing.Pipe()
            self.connections.append(ours)

            inited = service(its, self.logging_service.queue)
            self.services[inited.name] = (ours, inited)
            inited.start()
        
        self.main_loop()

    #now we just pass messages between processes
    def main_loop(self):
        while True:
            (read, write, exception) = select(self.connections, [], [])

            for ready in read:
                msg = read.recv()
                to = msg['to']
                self.services[to][0].send(msg)
