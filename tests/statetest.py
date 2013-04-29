import unittest

from bridge.services.model import states

class TestState(unittest.TestCase):
    def setUp(self):
        self.state = states.States(states.RangeStateCategory('bams', 0, 255))
        self.state.set_default_control('bams', lambda x : True)

    def test_default_control(self):
        self.assertTrue(self.state.get_control('bams', 45))

