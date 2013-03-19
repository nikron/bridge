import unittest

from bridge.services.io.insteon.idiom import InsteonIdiom

class TestInsteonIdiom(unittest.TestCase):
    def setUp(self):
        self.msg = ''
        def serv_func(method, real_id):
            self.msg = method + str(real_id)

        self.idiom = InsteonIdiom('test_service')
        self.idiom.charge(serv_func)

    def test_create_onoffasset(self):
        asset = self.idiom.create_asset(1, 'Home Appliance', 'ApplianceLinc V2')
        asset.perform_action('turn_on')

        self.assertEquals('turn_on1', self.msg)

