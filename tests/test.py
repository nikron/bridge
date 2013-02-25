#from ..device import Device, LampLinc
#from ..command import TurnOn

import unittest
from insteon_protocol.device import Device, LampLinc
from insteon_protocol.command.commands import TurnOn
from bridge.services.model.states import States, Trigger

class TestInsteonProtocol(unittest.TestCase):
    def setUp(self):
        self.device = LampLinc()

    def test_lamp_linc(self):
        self.assertEqual(self.device.encodeCommand(TurnOn, b"\x01\x02\x03"), b'\x02\x62\x01\x02\x03\x0f\x11\x00')


class TestState(unittest.TestCase):
    def setUp(self):
        self.flipped = False

        def flip():
            self.flipped = True

        trigger = Trigger('boom', 'bust', flip)
        self.state = States('boom', ['boom', 'bust'], [trigger])

    def test_flip_from_transition(self):
        self.state.transition('bust')
        self.assertTrue(self.flipped)
