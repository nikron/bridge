from bridge.service import BridgeService
from bottle import run, Bottle


class HTTPAPIService(BridgeService):
    def __init__(self, hub_con, log_queue, addr='127.0.0.1', port='8080'): 
        super().__init__('http_api', hub_con, log_queue)

        self.addr = addr
        self.port = port
        self.bottle = Bottle()

        self.bottle.get('/', self.bridge_information)

    def run(self):
        run(app=self.bottle, host=self.addr, port=self.port)

    def bridge_information(self):
        summary = self.remote_block_service_method('model', 'summary')
        return summary
