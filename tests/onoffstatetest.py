import unittest
from bridge.services.model.states import States, Trigger

class TestState(unittest.TestCase):
    def setUp(self):
        self.flipped = False

        def flip():
            self.flipped = True

        trigger = Trigger('bams', 'bust', flip)
        self.state = States(bams=['boom', 'bust'])
        self.state.add_trigger(trigger)

    def test_flip_from_transition(self):
        self.state.transition('bams', 'bust')
        self.assertTrue(self.flipped)
