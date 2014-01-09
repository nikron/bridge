"""
HTTP API for bridge, aims to be restful.
Don't blame me for globals, blame the library.
"""

from bridge.services import BridgeService, HTTP_API, MODEL
from bridge.model.attributes import verify_state
from external_libs.bottle import run, Bottle, request, response, HTTPError
from external_libs import mimeparse, jsonpatch
import logging
import json
import time
import uuid

JSON_MIME = 'application/json'
JSON_PATCH_MIME = 'application/json-patch+patch'

def accept_only_json(func):
    """
    Decorator for a function that checks if the current request.content_type is an acceptable for
    the HTTP method.

    :param func: Function to decorate.
    :type func: func

    :return: The decorated function.
    :rtype: func
    """
    acceptable = JSON_MIME
    acceptable_patch = JSON_PATCH_MIME

    def mime_okay(mimetype, acceptable=acceptable):
        """
        Returns whether the mimetype is within the acceptable one.

        :param mimetype: MIME to check
        :parma mimetype: str

        :param acceptable: Valid MIME.
        :type acceptable: str

        :rtype: bool
        """
        accept = mimeparse.best_match([acceptable], mimetype)
        return accept == acceptable

    def error_non_json(*args, **kwargs):
        """
        Inner function that raises error if mimetype not acceptable.
        """
        if request.method == 'GET':
            if not mime_okay(request.get_header('Accept', acceptable)):
                raise HTTPError(406, "Please accept {0}".format(acceptable))

        elif request.method == 'POST':
            if not mime_okay(request.content_type):
                raise HTTPError(415, "Only accepts {0}.".format(acceptable))

        elif request.method == 'PATCH':
            if not mime_okay(request.content_type, acceptable_patch):
                raise HTTPError(415, "Only accepts {0}.".format(acceptable_patch))

        return func(*args, **kwargs)

    return error_non_json

class HTTPAPIService(BridgeService):
    """
    Service to provide a http api to bridge.

    :param hub_con: Connectionto BridgeHub
    :type hub_con: Pipe

    :param addr:
    :type addr:

    :param port:
    :type port;

    :param debug:
    :type debug: bool
    """

    def __init__(self, config, hub_con, addr='0.0.0.0', port='8080', debug=True):
        super().__init__(HTTP_API, config, hub_con)

        self.addr = addr
        self.port = port
        self.bottle = Bottle(catchall=False, autojson=False)
        self.json = json.JSONEncoder(sort_keys=True, indent=4)

        self.bottle.get('/', callback=self.bridge_information())
        self.bottle.post('/', callback=self.bridge_save())
        self.bottle.get('/services', callback=self.services())
        self.bottle.get('/services/<service>', callback=self.service_info())
        self.bottle.get('/assets', callback=self.assets())

        self.bottle.get('/assets/<asset>', callback=self.get_asset_by_uuid())
        self.bottle.route('/assets/<asset>', method='PATCH', callback=self.change_asset_by_uuid())
        self.bottle.delete('/assets/<asset>', callback=self.delete_asset_by_uuid())

        self.bottle.post('/assets/<asset>/<action>', callback=self.post_action())
        self.bottle.get('/assets/<asset>/<action>', callback=self.get_asset_action())
        self.bottle.post('/assets', callback=self.create_asset())


    def run(self):
        failing = True
        while failing:
            try:
                run(app=self.bottle, host=self.addr, port=self.port, debug=True)
                failing = False #run exited for a reasonable reason

            except Exception:
                logging.exception("Net service errored out somehow.  Retrying in 5 seconds.")
                time.sleep(5)

    def bridge_information(self):
        """
        Return a function listing api urls.
        """
        @accept_only_json
        def inner_bridge_information():
            """
            Return api urls and model information.
            """
            base = request.url
            info = self.remote_block_service_method(MODEL, 'get_info')

            info['services_url'] = base + 'services/{service}'
            info['assets_url'] = base + 'assets/{asset uuid}'

            return self._encode(info)

        return inner_bridge_information

    def bridge_save(self):
        """
        Save the model information.
        """
        @accept_only_json
        def inner_bridge_save():
            """
            Inner method that makes the model save itself.
            """
            try:
                file_name = request.json['save']
            except KeyError:
                raise HTTPError(400, "Bad arguments.")
            except TypeError:
                raise HTTPError(400, "Bad arguments.")

            if not type(file_name) == str:
                raise HTTPError(400, "File name must be str")

            success, message = self.remote_block_service_method(MODEL, 'save', file_name)

            if success:
                response.status = 204
                return None
            else:
                HTTPError(500, message)

        return inner_bridge_save

    def services(self):
        """
        Function that output list of services.
        """
        @accept_only_json
        def inner_services():
            """
            Need to change the services to their url.
            """
            servs = self.remote_block_service_method(MODEL, 'get_io_services')
            servs_url_list = self._transform_to_urls(servs)

            return self._encode({ 'services' : servs_url_list })

        return inner_services

    def service_info(self):
        """
        Return a function that outputs JSON of service info.
        """
        @accept_only_json
        def inner_service_info(service):
            """
            Get service info from model; this might need to change to hub.
            """
            service = self.remote_block_service_method(MODEL, 'get_io_service_info', service)
            self._transform_to_urls(service, key='assets', newkey='asset_urls', prefix='assets/')

            if service:
                return self._encode(service)
            else:
                raise HTTPError(404, "Service not found.")

        return inner_service_info

    def assets(self):
        """
        Return a function that outputs JSON of the asset urls.
        """
        @accept_only_json
        def inner_assets():
            """
            Return url list of assets in JSON.
            """
            asset_uuids = self.remote_block_service_method(MODEL, 'get_assets')
            asset_urls = self._transform_to_urls(asset_uuids)
            return self._encode({ 'asset_urls' : asset_urls })

        return inner_assets

    def get_asset_by_uuid(self):
        """
        Return function that displays asset data.
        """
        @accept_only_json
        def inner_get_asset_by_uuid(asset):
            """
            Return JSON of an asset, replace actions with their urls.
            """
            asset_uuid = self._make_uuid(asset)
            return self._encode(self._get_asset_json(asset_uuid))

        return inner_get_asset_by_uuid

    def change_asset_by_uuid(self):
        """
        Change an asset.
        """
        @accept_only_json
        def inner_change_asset_by_uuid(asset):
            """
            :param asset: Asset to change
            :type asset: str
            """
            asset_uuid = self._make_uuid(asset)
            asset_json = self._get_asset_json(asset_uuid)

            change_name = False #it's only correct to do patch changes
            attribute_changes = [] #if the full patch is accepted

            patch = request.body.read(request.MEMFILE_MAX).decode()
            try:
                result = jsonpatch.apply_patch(asset_json, patch)
            except:
                raise HTTPError(400, "Not a correct json-patch.")

            changed = self._report_keys_changed(asset_json, result, {'name', 'attributes'})

            if 'name' in changed:
                if type(result['name']) == str:
                    change_name = True
                else:
                    raise HTTPError(422, "Name must be a string.")

            if 'attributes' in changed:
                attribute_changes = self._find_attribute_changes(asset_json, result)

            if change_name:
                logging.debug("Attempting to change name")
                self.remote_async_service_method(MODEL, 'set_asset_name', asset_uuid, changed['name'])
            for category, state in attribute_changes:
                logging.debug("Attempting to control")
                self.remote_async_service_method(MODEL, 'control_asset', asset_uuid, category, state)

            response.status = 204
            return None

        return inner_change_asset_by_uuid

    def delete_asset_by_uuid(self):
        """
        Delete an asset.
        """
        @accept_only_json
        def inner_delete_asset_by_uuid(asset):
            """
            :param asset: Asset to delete.
            :type asset: str
            """
            asset_uuid = self._make_uuid(asset)

            success = self.remote_block_service_method(MODEL, 'delete_asset', asset_uuid)

            if success:
                response.status = 204
                return None
            else:
                HTTPError(404, "Asset not found.")

        return inner_delete_asset_by_uuid

    def create_asset(self):
        """
        Return a function that outputs JSON of asset `name`.
        """
        @accept_only_json
        def inner_create_asset():
            """
            Attempt to create asset, must have submitted correct attributes in json form.
            """
            try:
                name = request.json['name']
                real_id = request.json['real id']
                asset_class = request.json['asset class']
                service = request.json['service']
            except KeyError:
                raise HTTPError(400, "Bad arguments.")
            except TypeError:
                raise HTTPError(400, "Bad arguments.")

            if not type(name) == type(real_id) == type(asset_class) == type(service) == str:
                raise HTTPError(400, "Asset attributes must be strings.")

            okay, msg = self.remote_block_service_method(MODEL, 'create_asset', name, real_id, service, asset_class)

            if okay:
                response.status = 201 #201 Created
                response.set_header('Location', request.url + "/" + str(msg))
                return self._encode({ 'message' : "Asset created." })

            else:
                raise HTTPError(400, msg)

        return inner_create_asset

    def get_asset_action(self):
        """
        Return function that retrieves info about action.
        """
        @accept_only_json
        def inner_get_asset_action(asset, action):
            """
            Get all actions of asset, output in json.
            """
            asset_uuid = self._make_uuid(asset)

            info = self.remote_block_service_method(MODEL, 'get_asset_action_info', asset_uuid, action)

            if info:
                return self._encode(info)

            else:
                raise HTTPError(404, "Action not found.")

        return inner_get_asset_action

    def post_action(self):
        """
        Return function for performing an action.
        """
        @accept_only_json
        def inner_post_action(asset, action):
            """
            Attempt to do action decribed by URL.
            """
            asset_uuid = self._make_uuid(asset)

            msg = self.remote_block_service_method(MODEL, 'perform_asset_action', asset_uuid, action)

            if not msg:
                return self._encode({ 'message' : "Action will be performed." })

            else:
                raise HTTPError(400, msg)

        return inner_post_action

    def _encode(self, obj):
        """
        Encode a python primitive collection to json, and set response encoding to json.

        :param obj: Object to encode
        :type obj: obj

        :return: Encoded byte string.
        :rtype: bytes
        """
        response.content_type = JSON_MIME
        return (self.json.encode(obj) + "\n").encode() #add a trailing newline

    def _get_asset_json(self, asset_uuid):
        """
        Get asset JSON, with an uuid in string form.

        :param asset_uuid: Asset to get inforamtion about.
        :type asset_uuid: uuid
        """
        asset_info = self.remote_block_service_method(MODEL, 'get_asset_info', asset_uuid)

        if asset_info:
            self._transform_to_urls(asset_info, key='uuid', newkey='url', prefix='assets/', delete=False)
            self._transform_to_urls(asset_info, key='actions', newkey='action_urls')
            asset_info['uuid'] = str(asset_info['uuid'])

            return asset_info

        else:
            raise HTTPError(404, "Asset not found.")

    def _transform_to_urls(self, container, **kwargs):
        """
        Transform a list to one appended with the current request.url, or a dict item
        to another dict key.
        """
        if 'prefix' in kwargs:
            prefix = request.urlparts[0] + '://' + request.urlparts[1] + '/' + kwargs['prefix']
        else:
            prefix = request.url

        if prefix[-1] != "/":
            prefix = prefix + "/"

        if type(container) == dict:
            key = kwargs['key']
            if 'newkey' in kwargs:
                newkey = kwargs['newkey']
            else:
                newkey = kwargs['newkey']

            container[newkey] = self._transform_to_urls(container[key], **kwargs)

            if newkey != key:
                if 'delete' in kwargs and kwargs['delete']:
                    del container[key]
                elif not 'delete' in kwargs:
                    del container[key]

            return container

        elif type(container) == list:
            return [prefix + str(item) for item in container]
        else:
            return prefix + str(container)

    def _find_attribute_changes(self, orginal, new):
        attribute_json = orginal['attributes']
        new = new['attributes']

        allowable = {category for category in attribute_json if attribute_json[category]['controllable']}
        categories_changed = self._report_keys_changed(attribute_json, new, allowable)

        changes = []

        for category in categories_changed:
            self._report_keys_changed(attribute_json[category], new[category], {'current'})
            current_state = new[category]['current']

            current_state = verify_state(attribute_json[category], current_state)
            if current_state is not None:
                changes.append((category, current_state))
            else:
                raise HTTPError(422, "Current was not a possible state.")

        return changes

    @staticmethod
    def _make_uuid(asset):
        """
        Check if uuid `asset` is valid, raise HTTPerror if it isn't.
        """
        try:
            asset_uuid = uuid.UUID(asset)
        except ValueError:
            raise HTTPError(404, "Asset not found/not valid UUID.")

        return asset_uuid

    @staticmethod
    def _report_keys_changed(first, second, allowable):
        """
        Find the which keys between the first and secondary dictionaries, and error if
        some of the keys are not in the allowable set.

        :param first: First dictionary
        :type first: dict

        :param second: Second dictionary
        :type second: dict

        :param allowable: Set of keys that can change
        :type allowable: set
        """
        first_set = set(first.keys())
        second_set = set(second.keys())
        changed = {key for key in first_set.intersection(second_set) if first[key] != second[key]}
        changed.union(first_set.symmetric_difference(second_set))

        if not changed.issubset(allowable):
            raise HTTPError(422, "Patching something that can't be patched.")

        return changed
