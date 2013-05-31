"""
Test assets.
"""
import unittest
from bridge.model.states import States, Trigger
from bridge.model.assets import OnOffAsset
from bridge.model.actions import perform_action

class TestAsset(unittest.TestCase):
    def setUp(self):
        self.trans = False

        def trigger():
            self.trans = True


        trigger = Trigger('main', True, trigger)

        self.asset = OnOffAsset('hi', 'null', 'test_service', 'boop')
        self.asset.add_trigger(trigger)

    def test_on(self):
        ret = perform_action(self.asset, 'turn_on')
        self.assertEquals(ret.method, 'turn_on')

    def test_off(self):
        ret = perform_action(self.asset, 'turn_off')
        self.assertEquals(ret.method, 'turn_off')

    def test_trigger(self):
        self.asset.transition('main', True)
        self.assertTrue(self.trans)

    def test_get_real_id(self):
        self.assertEquals(self.asset.get_real_id(), 'null')
