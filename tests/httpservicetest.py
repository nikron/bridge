"""
Test http service
"""

import unittest
from multiprocessing import Pipe
from bridge.services.net.http_service import HTTPAPIService
from bridge.services import BridgeMessage
from external_libs.bottle import HTTPError, response 

import uuid

class TestHTTPService(unittest.TestCase):
    def setUp(self):
        (ours, its) = Pipe()

        self.serv = HTTPAPIService(its)
        self.ours = ours

    def test_info(self):
        self.ours.send(BridgeMessage('http_api', 'reply', None, None, None, {}))
        api = self.serv.bridge_information()()
        self.assertIsNotNone(api)

    def test_valid_uuid(self):
        self.assertRaises(HTTPError, self.serv._make_uuid, 'afadf')

    def test_create_asset(self):
        self.assertRaises(HTTPError, self.serv.create_asset())

    def test_transform_to_urls(self):
        self.assertEquals('http://127.0.0.1/boo', self.serv._transform_to_urls('boo'))

    def test_delete_asset_by_uuid(self):
        self.ours.send(BridgeMessage('http_api', 'reply', None, None, None, True))
        self.serv.delete_asset_by_uuid()(str(uuid.uuid1()))
        self.assertEquals(response.status, '204 No Content')

    def test_report_keys_changed(self):
        first = {1 : 2, 3 : 4, 6 : 8}
        second = {1 : 2, 3 : 4, 6 : 9}
        allowable = {6}
        report = self.serv._report_keys_changed(first, second, allowable)
        self.assertEquals(report, allowable)

