import unittest
from insteon_protocol.device import Device, LampLinc
from insteon_protocol.command.commands import TurnOn

class TestInsteonProtocol(unittest.TestCase):
    def setUp(self):
        self.device = LampLinc()

    def test_lamp_linc(self):
        self.assertEqual(self.device.encodeCommand(TurnOn, b"\x01\x02\x03"), b'\x02\x62\x01\x02\x03\x0f\x11\x00')
