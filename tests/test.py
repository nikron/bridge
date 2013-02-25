#from ..device import Device, LampLinc
#from ..command import TurnOn

import unittest
from bridge.services.insteon.command_encode.device import Device, LampLinc
from bridge.services.insteon.command_encode.device import TurnOn

class TestInsteonProtocol(unittest.TestCase):
    def setUp(self):
        self.device = LampLinc()

    def test_lamp_linc(self):
        self.assertEqual(self.device.encodeCommand(TurnOn, "010203"), b"0262010203001200")
        self.assertTrue(self.device.decodeCommand("0x026201020300120006").get("ack"))
        self.assertFalse(self.device.decodeCommand("0x026201020300120015").get("ack"))
