import unittest

from bridge.services.io.insteon.idiom import InsteonIdiom
from bridge.services.model.actions import perform_action

class TestInsteonIdiom(unittest.TestCase):
    def setUp(self):
        self.msg = ''
        def serv_func(method, real_id):
            self.msg = method + real_id

        self.idiom = InsteonIdiom('test_service')
        self.idiom.charge(serv_func)
        self.fake_real_id = "bbbbbb"

    def test_create_onoffasset(self):
        asset = self.idiom.create_asset('Home Appliance', self.fake_real_id, 'ApplianceLinc V2')
        perform_action(asset, 'turn_on')

        self.assertEquals('turn_on' + self.fake_real_id, self.msg)

