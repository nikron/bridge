import unittest
import upb

class TestAsset(unittest.TestCase):
    def test_goto_direct(self):
        ascii_packet = upb.UPBGoToLevel(52, 100).construct_packet()
        self.assertEquals(ascii_packet, b'081c0134ff226422')


