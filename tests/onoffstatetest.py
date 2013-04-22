import unittest
from bridge.services.model.states import States, Trigger

class TestState(unittest.TestCase):
    def setUp(self):
        self.flipped = False

        def flip():
            self.flipped = True

        trigger = Trigger('bams', True, flip)
        self.state = States(bams=bool)
        self.state.add_trigger(trigger)

    def test_flip_from_transition(self):
        self.state.transition('bams', True)
        self.assertTrue(self.flipped)
