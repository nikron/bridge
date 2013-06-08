import unittest
import binascii
from upb import registers, UPBMessage

class TestAsset(unittest.TestCase):
    def setUp(self):
        self.setup = registers.RegisterDescription(registers.SETUP)

    def test_is_report(self):
        reg_report = bytes([0x0A, 0x00, 0xff, 0xff, 0x01, 0x90, 0x00, 0xff,
            0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00,
            0x22, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0xff])
        reg_report = binascii.hexlify(reg_report)
        reg_msg = UPBMessage.create_from_packet(reg_report)

        self.assertTrue(self.setup.is_report(reg_msg))


    def test_correct_dest(self):
        msg = self.setup.create_get_registers(network_id = 1, destination_id = 52)
        self.assertEquals(msg.destination_id, 52)

