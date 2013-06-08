import unittest
import json

from bridge.model import attributes

class TestState(unittest.TestCase):
    def setUp(self):
        self.attributes = attributes.Attributes(attributes.IntegerAttribute('bams', 0, 255),
                attributes.ASCIIAttribute('huh', 16))
        self.attributes.set_default_control('bams', lambda x : True)
        def control_func(x):
            if x == b'true':
                return True
            else:
                return False
        self.attributes.set_default_control('huh', control_func)

    def test_default_control(self):
        self.assertTrue(self.attributes.get_control('bams', 45))

    def test_serializable(self):
        serial = self.attributes.serializable()
        serial = json.dumps(serial)
        serial = json.loads(serial)

        self.assertTrue(serial['bams']['controllable'])

    def test_bytes(self):
        self.assertTrue(self.attributes.get_control('huh', b'true'))
