"""
Test the insteon idiom functionality.
"""
import unittest

from bridge.services.io.insteon.idiom import InsteonIdiom
from bridge.services.model.actions import perform_action

class TestInsteonIdiom(unittest.TestCase):
    def setUp(self):
        self.idiom = InsteonIdiom('test_service')
        self.fake_real_id = "bbbbbb"

    def test_create_onoffasset(self):
        asset = self.idiom.create_asset('Home Appliance', self.fake_real_id, 'ApplianceLinc V2')
        ret = perform_action(asset, 'turn_on')

        self.assertEquals('test_service', ret.to)
