import unittest

from bridge import upb

class TestModel(unittest.TestCase):
    def test_upb_id(self):
        real_id = upb.upb_id_to_real_id(1, 85)
        self.assertEquals(real_id, '1.85')

    def test_real_id(self):
        net, dest = upb.real_id_to_upb_id('1.85')
        self.assertEquals(net, 1)
        self.assertEquals(dest, 85)
