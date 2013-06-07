import unittest
import upb

class TestAsset(unittest.TestCase):
    def test_goto_direct(self):
        message = upb.UPBGoToLevel(100, ack_pulse = False, ack_message = True, destination_id = 52)
        ascii_packet = message.construct_ascii_packet()
        self.assertEquals(ascii_packet, b'081c0134ff226422')
