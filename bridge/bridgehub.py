import multiprocessing
import bridgelogging
from bridgeservice import CLOSE_MESSAGE, DEBUG_MESSAGE
from services.io.io_types import IOConfig
from services.model.model_service import ModelService
from select import select

class BridgeHub():
    def __init__(self, configuration, *args, **kwargs):
        self.logging_service = bridgelogging.LoggingService()
        self.configuration = configuration
        self.connections = []
        self.services = {}

        self.model_config = { 
                                'storage' : configuration.model_driver,
                                'io_services' : []
                             }

    def create_connection(self):
        (its, ours) = multiprocessing.Pipe()
        self.connections.append(ours)
        return its

    def add_service(self, conn, service):
        self.services[service.name] = (conn, service)
        
    def start_model(self):
        conn = self.create_connection()
        service = ModelService(self.model_config, conn, self.logging_service.queue)
        self.add_service(conn, service)

    def start_io_services(self):
        for io_config_args in self.configuration.io_services:
            conn = self.create_connection() 

            io_config = IOConfig(*io_config_args)
            io_service =  io_config.create_service(conn, self.logging_service.queue)

            self.add_service(conn, io_service)
            self.model_config['io_services'].append(io_config.model_information())

            io_service.start()

    def run(self):
        #start the logging process immediately
        self.logging_service.start()
        bridgelogging.service_configure_logging(self.logging_service.queue)
        
        #start each service
        self.start_io_services()
        self.start_model()
        
        self.main_loop()

    #now we just pass messages between processes
    def main_loop(self):
        spinning = True
        while spinning:
            try:
                (read, write, exception) = select(self.connections, [], [])
                for ready in read:
                    msg = ready.recv()
                    to = msg['to']
                    self.services[to][0].send(msg)

            except KeyboardInterrupt:
                for con in self.connections:
                    con.send(CLOSE_MESSAGE)

                spinning = False

        #this errors for some reason
        #for service in self.services.values():
        #    service[1].join()
