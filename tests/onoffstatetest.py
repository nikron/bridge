import unittest
from bridge.model.attributes import Attributes, BinaryAttribute

class TestState(unittest.TestCase):
    def setUp(self):
        def flip(attribute):
            return lambda : attribute.change('bams', True)

        self.attributes = Attributes(BinaryAttribute('bams'))
        self.attributes.set_control('bams', True, flip(self.attributes))

    def test_flip_from_control(self):
        control = self.attributes.get_control('bams', True)
        control()
        self.assertTrue(self.attributes.attributes['bams'].current_state)
