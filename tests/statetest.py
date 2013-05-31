import unittest

from bridge.model import states

class TestState(unittest.TestCase):
    def setUp(self):
        self.state = states.States(states.IntegerRangeStateCategory('bams', 0, 255))
        self.state.set_default_control('bams', lambda x : True)

    def test_default_control(self):
        self.assertTrue(self.state.get_control('bams', 45))

    def test_serializable(self):
        serial = self.state.serializable()

        self.assertTrue(serial['bams']['controllable'])
