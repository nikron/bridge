#from ..device import Device, LampLinc
#from ..command import TurnOn

import unittest
from bridge.services.insteon.insteon_im_protocol.device import Device, LampLinc
from bridge.services.insteon.insteon_im_protocol.command.command import TurnOn

class TestInsteonProtocol(unittest.TestCase):
    def setUp(self):
        self.device = LampLinc()

    def test_lamp_linc(self):
        self.assertEqual(self.device.encodeCommand(TurnOn, b"\x01\x02\x03"), b'\x02\x62\x01\x02\x03\x0f\x11\x00')
        self.assertTrue(self.device.decodeCommand("0x026201020300120006").get("ack"))
        self.assertFalse(self.device.decodeCommand("0x026201020300120015").get("ack"))
