"""
HTTP API for bridge, aims to be restful.
Don't blame me for globals, blame the library.
"""

from bridge.service import BridgeService
from bridge.services import MODEL
from external_libs import bottle, mimeparse, jsonpatch
from external_libs.bottle import request, response, HTTPError
import json
import logging
import uuid

#
# Utility code
#

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
        Checks if the mimetype is acceptable.
        """
        accept = mimeparse.best_match([acceptable], mimetype)
        return accept == acceptable

    def error_non_json(*args, **kwargs):
        """
        Inner function that raises error if mimetype not acceptable.
        """
        if request.method == 'GET':
            if not mime_okay(request.get_header('Accept', acceptable)):
                raise HTTPError(406, "Please accept `{0}`".format(acceptable))

        elif request.method == 'POST':
            if not mime_okay(request.content_type):
                raise HTTPError(415, "Only accepts application/json.")

        elif request.method == 'PATCH':
            if not mime_okay(request.content_type, acceptable_patch):
                raise HTTPError(415, "Only accepts application/json-patch.")

        return func(*args, **kwargs)

    return error_non_json

#
# Request handlers 
#

_app = bottle.Bottle(catchall=False, autojson=False)
_svc = None

@_app.get("/")
@accept_only_json
def _bridge_information():
    """Inner method."""
    base = request.url
    info = _svc.remote_block_service_method(MODEL, 'get_info')

    info['services_url'] =  base + 'services/{service}'
    info['assets_url'] =  base + 'assets/{asset uuid}'

    return _svc.encode(info)

    return inner_bridge_information

@_app.post("/")
@accept_only_json
def _bridge_save(_svc):
    """Inner method."""
    try:
        file_name = request.json['save']
    except KeyError:
        raise HTTPError(400, "Bad arguments.")
    except TypeError:
        raise HTTPError(400, "Bad arguments.")

    if not type(file_name) == str:
        raise HTTPError(400, "File name must be str")

    success, message = _svc.remote_block_service_method(MODEL, 'save', file_name)

    if success:
        return _svc.encode({ 'message' : message })
    else:
        HTTPError(500, message)

@_app.get("/services")
@accept_only_json
def _services():
    """Need to change the services to their url."""
    servs = _svc.remote_block_service_method(MODEL, 'get_io_services')
    servs_url_list = _svc.transform_to_urls(servs)

    return _svc.encode({ 'services' : servs_url_list })

@_app.get("/services/<service>")
@accept_only_json
def _service_info(service):
    """Get service info from model; this might need to change to hub."""
    service = _svc.remote_block_service_method(MODEL, 'get_io_service_info', service)
    _svc.transform_to_urls(service, key='assets',  newkey='asset_urls', prefix='assets/')

    if service:
        return _svc.encode(service)
    else:
        raise HTTPError(404, "Service not found.")

@_app.get("/assets")
@accept_only_json
def _assets():
    """Return url list of assets in JSON."""
    asset_uuids = _svc.remote_block_service_method(MODEL, 'get_assets')
    asset_urls = _svc.transform_to_urls(asset_uuids)

    return _svc.encode({ 'asset_urls' : asset_urls })

@_app.get("/assets/<asset>")
@accept_only_json
def _get_asset_by_uuid(asset):
    """Return JSON of an asset, replace actions with their urls."""
    asset_uuid = _svc._make_uuid(asset)
    return _svc.encode(_svc._get_asset_json(asset_uuid))

@_app.route("/assets/<asset>", method="PATCH")
@accept_only_json
def _change_asset_by_uuid(asset):
    asset_uuid = _svc._make_uuid(asset)
    asset_json = _svc._get_asset_json(asset_uuid)

    change_name = False #it's only correct to do patch changes
    state_changes = [] #if the full patch is accepted

    patch = request.body.read(request.MEMFILE_MAX).decode()
    try:
        result = jsonpatch.apply_patch(asset_json, patch)
    except jsonpatch.JsonPatchException:
        raise HTTPError(400, "Not a correct json-patch.")

    changed = _svc._report_keys_changed(asset_json, result, {'name', 'state'})

    if 'name' in changed:
        if type(result['name']) == str:
            change_name = True
        else:
            raise HTTPError(422, "Name must be a string.")

    #check if state is changed in a valid way, it's a bit of a doozy
    #can't think of better way to do it (except with like a state_url so this makes
    #sense in its own method
    if 'state' in changed:
        state_json = asset_json['state']
        allowable = {category for category in state_json if state_json[category]['controllable']}
        categories_changed = _svc._report_keys_changed(state_json, result['state'], allowable)

        for category in categories_changed:
            _svc._report_keys_changed(state_json[category], result['state'][category], {'current'})
            current_state = result['state'][category]['current']

            if current_state in result['state'][category]['possible states']:
                state_changes.append((category, current_state))
            else:
                raise HTTPError(422, "Current must be a string.")

    if change_name:
        logging.debug("Attempting to change name")
        _svc.remote_async_service_method(MODEL, 'set_asset_name', asset_uuid, changed['name'])
    for state_change in state_changes:
        logging.debug("Attempting to control")
        _svc.remote_async_service_method(MODEL, 'control_asset', asset_uuid, state_change[0], state_change[1])

    response.status = 204
    return None

@_app.delete("/assets/<asset>")
@accept_only_json
def _delete_asset_by_uuid(asset):
    asset_uuid = _svc._make_uuid(asset)

    success = _svc.remote_block_service_method(MODEL, 'delete_asset', asset_uuid)

    if success:
        response.status = 204
        return None
    else:
        HTTPError(404, "Asset not found.")

@_app.post("/assets")
@accept_only_json
def _create_asset():
    """Attempt to create asset, must have submitted correct attributes in json form."""
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

    okay, msg = _svc.remote_block_service_method(MODEL, 'create_asset', name, real_id, service, asset_class)

    if okay:
        response.status = 201 #201 Created
        response.set_header('Location', request.url + "/" + str(msg))
        return _svc.encode({ 'message' : "Asset created." })

    else:
        raise HTTPError(400, msg)

@_app.get("/assets/<asset>/<action>")
@accept_only_json
def _get_asset_action(asset, action):
    """Get all actions of asset, output in json."""
    asset_uuid = _svc._make_uuid(asset)

    info = _svc.remote_block_service_method(MODEL, 'get_asset_action_info', asset_uuid, action)

    if info:
        return _svc.encode(info)

    else:
        raise HTTPError(404, "Action not found.")

@_app.post("/assets/<asset>/<action>")
@accept_only_json
def _post_action(asset, action):
    """Attempt to do action decribed by URL."""
    asset_uuid = _svc._make_uuid(asset)

    msg = _svc.remote_block_service_method(MODEL, 'perform_asset_action', asset_uuid, action)

    if not msg:
        return _svc.encode({ 'message' : "Action will be performed." })

    else:
        raise HTTPError(400, msg)

#
# Listener service
#

class HTTPAPIService(BridgeService):
    """
    Service to provide a http api to bridge.
    """

    def __init__(self, hub_con, addr='0.0.0.0', port='8080', debug=True): 
        super().__init__('http_api', hub_con)
        self.addr = addr
        self.port = port
        self.json = json.JSONEncoder(sort_keys=True, indent=4)

    def run(self):
        global _svc
        if _svc != None:
            raise RuntimeError("Only one HTTPAPIService may be run at a time")
        _svc = self
        bottle.run(app=_app, host=self.addr, port=self.port, debug=True)
        _svc = None

    def encode(self, obj):
        """
        Encode a python primitive collection to json, and set response encoding to json.
        """
        response.content_type = JSON_MIME
        return (self.json.encode(obj) + "\n").encode() #add a trailing newline
    
    def _get_asset_json(asset_uuid):
        """Get asset JSON, with an uuid in string form."""
        asset_info = self.remote_block_service_method(MODEL, 'get_asset_info', asset_uuid)

        if asset_info:
            self.transform_to_urls(asset_info, key='uuid', newkey='url', prefix='assets/', delete=False)
            self.transform_to_urls(asset_info, key='actions', newkey='action_urls')
            asset_info['uuid'] = str(asset_info['uuid'])

            return asset_info

        else:
            raise HTTPError(404, "Asset not found.")

    def _report_keys_changed(first, second, allowable):
        first_set = set(first.keys())
        second_set = set(second.keys())
        changed = {key for key in first_set.intersection(second_set) if first[key] != second[key]}
        changed.union(first_set.symmetric_difference(second_set))

        if changed.issubset(allowable):
            HTTPError(422, "Patching something that can't be patched.")

        return changed

    @staticmethod
    def _make_uuid(asset):
        """Check if uuid `asset` is valid, raise HTTPerror if it isn't."""
        try:
            asset_uuid = uuid.UUID(asset)
        except ValueError:
            raise HTTPError(404, "Asset not found/not valid UUID.")

        return asset_uuid

    def transform_to_urls(self, container, **kwargs):
        """Transform a list to one appended with the current request.url, or a dict item
        to another dict key."""
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

            container[newkey] = self.transform_to_urls(container[key], **kwargs)

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
