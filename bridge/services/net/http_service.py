from bridge.service import BridgeService
from bottle import run, Bottle, request
import logging

class HTTPAPIService(BridgeService):

    def __init__(self, hub_con, log_queue, addr='127.0.0.1', port='8080', debug=True): 
        super().__init__('http_api', hub_con, log_queue)

        self.addr = addr
        self.port = port
        self.bottle = Bottle(catchall=False)

        self.bottle.get('/', callback=self.bridge_information())
        self.bottle.get('/services', callback=self.services())
        self.bottle.get('/assets', callback=self.assets())

    def run(self):
        run(app=self.bottle, host=self.addr, port=self.port, debug=True)

    def bridge_information(self):
        """
        Return a function listing api urls.
        """
        def info():
            base = request.url

            api = {
                    'services_url' : base + 'services/{service}',
                    'assets_url' : base + 'assets/{asset uuid}'
                   }

            return api

        return info

    def services(self):
        def serv():
            servs = self.remote_block_service_method('model', 'get_services')

            return { 'services' : servs }
        return serv

    def assets(self):
        def a():
            asset_uuids = self.remote_block_service_method('model', 'get_assets')

            return { 'assets' : asset_uuids }

        return a
