import unittest
from multiprocessing import Pipe
from bridge.services.net.http_service import HTTPAPIService
from bridge.service import BridgeMessage
from bottle import HTTPError

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
        self.assertRaises(HTTPError, self.serv._check_valid_uuid, 'afadf')

    def test_create_asset(self):
        self.assertRaises(HTTPError, self.serv.create_asset())
