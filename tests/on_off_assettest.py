import unittest
from bridge.services.model.states import States, Trigger
from bridge.services.model.assets import Asset, OnOffAsset

class TestOnOffAsset(unittest.TestCase):
    def setUp(self):
        self.flipped = False

        def flip():
            self.flipped = True

        trigger1 = Trigger('unknown', 'pending off', flip)
        trigger2 = Trigger('unknown', 'pending on', flip)
        self.asset = OnOffAsset(1, [trigger1, trigger2])

    def test_flip_from_turn_off(self):
        self.asset.turn_off()
        self.assertTrue(self.flipped)

    def test_flip_from_turn_on(self):
        self.asset.turn_on()
        self.assertTrue(self.flipped)
