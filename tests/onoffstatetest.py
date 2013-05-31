import unittest
from bridge.model.states import States, BinaryStateCategory, Trigger

class TestState(unittest.TestCase):
    def setUp(self):
        self.flipped = False

        def flip():
            self.flipped = True

        trigger = Trigger('bams', True, flip)
        self.state = States(BinaryStateCategory('bams'))
        self.state.add_trigger(trigger)

    def test_flip_from_transition(self):
        self.state.transition('bams', True)
        self.assertTrue(self.flipped)

    def test_flip_from_sudden(self):
        self.state.sudden_transition('bams', True)
        self.assertFalse(self.flipped)
