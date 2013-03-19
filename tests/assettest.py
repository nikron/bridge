import unittest
from bridge.services.model.states import States, Trigger
from bridge.services.model.assets import OnOffAsset, OnOffBacking

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
        backing = OnOffBacking(1, flip, floop)

        self.asset = OnOffAsset('hi', backing)

    def test_on(self):
        self.asset.perform_action('turn_on')
        self.assertTrue(self.flipped)

    def test_off(self):
        self.asset.perform_action('turn_off')
        self.assertTrue(self.flooped)
