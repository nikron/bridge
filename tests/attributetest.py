import unittest

from bridge.model import attributes

class TestState(unittest.TestCase):
    def setUp(self):
        self.attributes = attributes.Attributes(attributes.IntegerRangeAttribute('bams', 0, 255))
        self.attributes.set_default_control('bams', lambda x : True)

    def test_default_control(self):
        self.assertTrue(self.attributes.get_control('bams', 45))

    def test_serializable(self):
        serial = self.attributes.serializable()

        self.assertTrue(serial['bams']['controllable'])
