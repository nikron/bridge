import unittest
from bridge.services.model.states import States, Trigger

class TestState(unittest.TestCase):
    def setUp(self):
        self.flipped = False

        def flip():
            self.flipped = True

        trigger = Trigger('boom', 'bust', flip)
        self.state = States('boom', ['boom', 'bust'], [trigger])

    def test_flip_from_transition(self):
        self.state.transition('bust')
        self.assertTrue(self.flipped)
