import unittest
from insteon_protocol.device import *

class DeviceTestCase(unittest.TestCase):

	def testFanLinc(self):
		device = FanLinc

	def testLampLinc(self):
		device = LampLinc
		#self.assertEqual(self.device.encodeCommand(TurnOn, b"\x01\x02\x03"), b'\x02\x62\x01\x02\x03\x0f\x11\x00')

	def testIOLinc(self):
		device = IOLinc
