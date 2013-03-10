import unittest
from bridge.services.model.states import States, Trigger
from bridge.services.model.assets import Asset, OnOffAsset

class TestAsset(unittest.TestCase):
    def setUp(self):
        self.flipped = False

        def flip():
            self.flipped = True

        trigger1 = Trigger('boom', 'bust', flip)
        trigger2 = Trigger('boom', 'blip', flip)
        self.asset = Asset(1, 'boom', ['boom', 'bust', 'blip'], ['boom', 'bust'], [trigger1, trigger2])

    def test_flip_from_transition(self):
        self.asset.transition('blip')
        self.assertTrue(self.flipped)

    def test_flip_from_outside_transition(self):
        self.asset.outside_transition('blip')
        self.assertFalse(self.flipped)

        self.asset.outside_transition('bust')
        self.assertTrue(self.flipped)
