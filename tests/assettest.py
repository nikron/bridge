import unittest
from bridge.services.model.states import States, Trigger
from bridge.services.model.assets import OnOffAsset, OnOffBacking
from bridge.services.model.actions import perform_action

class TestAsset(unittest.TestCase):
    def setUp(self):
        self.flipped = False
        self.flooped = False
        self.trans = False

        def flip():
            self.flipped = True

        def floop():
            self.flooped = True

        def trigger():
            self.trans = True


        trigger = Trigger('bums', 'bust', trigger)
        backing = OnOffBacking(1, "Test Asset", flip, floop)

        self.asset = OnOffAsset('hi', backing)

    def test_on(self):
        perform_action(self.asset, 'turn_on')
        self.assertTrue(self.flipped)

    def test_off(self):
        perform_action(self.asset, 'turn_off')
        self.assertTrue(self.flooped)
