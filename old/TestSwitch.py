import random
import unittest
import mock_switch

class TestSwitch(unittest.TestCase):

    def TestInitialState(self):
        switch = MockSwitch()
        assert (switch.get_state() = True)
        
    def TestToggle(self):
        switch = MockSwitch()
        switch.toggle()
        assert (switch.get_state() = False)
        
    def TestTurnOn(self):
        switch = MockSwitch()
        switch.turn_on()
        assert (switch.get_state() = True)
        
    def TestTurnOff(self):
        switch = MockSwitch()
        switch.turn_off()
        assert (switch.get_state() = False)
        
