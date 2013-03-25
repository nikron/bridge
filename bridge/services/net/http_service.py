"""
HTTP API for bridge, aims to be restful.
Don't blame me for globals, blame the library.
"""

from bridge.service import BridgeService
from bottle import run, Bottle, request, response, HTTPError
import mimeparse

import uuid

def accept_only_json(func):
    """Raise an error if content type isn't json."""
    acceptable = 'application/json'

    def mime_okay(mimetype):
        """Checks if the mimetype is acceptable."""
        accept = mimeparse.best_match([acceptable], mimetype)
        return accept == acceptable

    def error_non_json(*args, **kwargs):
        """Inner function that raises error if mimetype not acceptable."""
        if request.method == 'GET':
            if not mime_okay(request.get_header('Accept', acceptable)):
                raise HTTPError(406, "Please accept `{0}`".format(acceptable))

        elif request.method == 'POST':
            if not mime_okay(request.content_type):
                raise HTTPError(415)

        return func(*args, **kwargs)

    return error_non_json

class HTTPAPIService(BridgeService):
    """Service to provide a http api to bridge."""

    def __init__(self, hub_con, addr='0.0.0.0', port='8080', debug=True): 
        super().__init__('http_api', hub_con)

        self.addr = addr
        self.port = port
        self.bottle = Bottle(catchall=False)

        self.bottle.get('/', callback=self.bridge_information())
        self.bottle.get('/services', callback=self.services())
        self.bottle.get('/services/<service>', callback=self.service_info())
        self.bottle.get('/assets', callback=self.assets())
        self.bottle.get('/assets/<asset>', callback=self.get_asset_from_uuid())
        #self.bottle.post('/assets/<asset>/<action>', callback=self.post_action())
        self.bottle.get('/assets/<asset>/<action>', callback=self.get_asset_action())
        self.bottle.post('/assets', callback=self.create_asset())


    def run(self):
        run(app=self.bottle, host=self.addr, port=self.port, debug=True)


    def bridge_information(self):
        """
        Return a function listing api urls.
        """
        @accept_only_json
        def inner_bridge_information():
            """Inner method."""
            base = request.url

            api = {
                    'services_url' : base + 'services/{service}',
                    'assets_url' : base + 'assets/{asset uuid}'
                   }

            return api

        return inner_bridge_information

    def services(self):
        @accept_only_json
        def inner_services():
            servs = self.remote_block_service_method('model', 'get_services')
            servs_url_list = []

            for serv in servs:
                servs_url_list.append(request.url + "/" + serv)

            return { 'services' : servs_url_list }

        return inner_services

    def service_info(self):
        @accept_only_json
        def inner_service_info(service):
            service = self.remote_block_service_method('model', 'get_service_info', service)

            if service:
                return service
            else:
                raise HTTPError(404, "Service not found.")

        return inner_service_info

    def assets(self):
        """Return a function that outputs JSON of the asset urls."""

        @accept_only_json
        def inner_assets():
            asset_uuids = self.remote_block_service_method('model', 'get_assets')
            asset_url_list = []

            for uuid in asset_uuids:
                asset_url_list.append(request.url + "/" + str(uuid))

            return { 'assets_urls' : asset_url_list }

        return inner_assets

    def get_asset_from_uuid(self):

        @accept_only_json
        def inner_get_asset_from_uuid(asset):
            asset_uuid = self.check_valid_uuid(asset)

            asset = self.remote_block_service_method('model','get_asset_info', asset_uuid)

            if asset:
                asset['action_urls'] = []
                for action in asset['actions']:
                    asset['action_urls'].append(request.url + "/" + action)
                del asset['actions']

                return asset
            else:
                raise HTTPError(404, "Asset not found.")

        return inner_get_asset_from_uuid

    def create_asset(self):
        """Return a function that outputs JSON of asset `name`."""

        @accept_only_json
        def inner_create_asset():
            name = request.json['name']
            real_id = request.json['real id']
            asset_class = request.json['asset class']
            service = request.json['service']

            if not type(name) == type(real_id) == type(asset_class) == type(service) == str:
                raise HTTPError(400, "Asset attributes must be strings.")

            okay, msg = self.remote_block_service_method('model', 'create_asset', name, real_id, service, asset_class)

            if not okay:
                raise HTTPError(400, msg)
            else:
                response.status = 201 #201 Created
                response.set_header('Location', request.url + "/" + str(msg))
                return { "message" : "Asset created." }

        return inner_create_asset

    def get_asset_action(self):
        """Return function that retrives info about action."""

        @accept_only_json
        def inner_get_asset_action(asset, action):
            asset_uuid = self.check_valid_uuid(asset)

            info = self.remote_block_service_method('model', 'get_asset_action_info', asset_uuid, action)

            if info:
                return info
            else:
                raise HTTPError(404, "Action not found.")

        return inner_get_asset_action

    def post_action(self):

        @accept_only_json
        def inner_post_action(asset, action):
            asset_uuid = self.check_valid_uuid(asset)

            msg = self.remote_block_service_method('model', 'perform_asset_action', asset_uuid, action)

            if msg:
                return { "message" : "Action will be performed." }
            else:
                raise HTTPError(400, msg)

        return inner_post_action


    def check_valid_uuid(self, asset):
        try:
            asset_uuid = uuid.UUID(asset)
        except ValueError:
            raise HTTPError(404, "Asset not found/not valid UUID.")

        return asset_uuid

