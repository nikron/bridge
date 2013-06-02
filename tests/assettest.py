"""
Test assets.
"""
import unittest
from bridge.model.assets.basic_assets import OnOffAsset
from bridge.model.actions import perform_action

class TestAsset(unittest.TestCase):
    def setUp(self):
        self.trans = False

        self.asset = OnOffAsset('hi', 'null', 'test_service', 'boop')

    def test_on(self):
        ret = perform_action(self.asset, 'turn_on')
        self.assertEquals(ret.method, 'turn_on')

    def test_off(self):
        ret = perform_action(self.asset, 'turn_off')
        self.assertEquals(ret.method, 'turn_off')

    def test_get_real_id(self):
        self.assertEquals(self.asset.get_real_id(), 'null')
