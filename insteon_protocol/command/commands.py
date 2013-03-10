"""
Create an Insteon command by calling the appriate object
with the correct information.
"""
from abc import ABCMeta, abstractmethod
import bitstring #maybe get rid of this depedance but it makes things easier
import logging

class Command():
    __metaclass__ = ABCMeta

    @abstractmethod
    def encode(self):
        pass


class InsteonCommand(Command):
    """Base class for all insteon commands."""

    def __init__(self, to_address, from_address, broadcast, group, ack, extended, max_hops, cmd1, cmd2, extended_data):
        self.to_address = from_address
        self.from_address = from_address

        self.broadcast = broadcast
        self.group = group
        self.ack = ack
        self.extended = extended
        self.max_hops = max_hops
        self.cmd1 = cmd1
        self.cmd2 = cmd2
        self.extended_data = extended_data

        self.cmd_bytes = cmd1 + cmd2


    def create_flag(self):
        """Create the message flag byte."""
        flag_byte = bitstring.BitString(8)
        flag_byte[0] = self.broadcast
        flag_byte[1] = self.group
        flag_byte[2] = self.ack
        flag_byte[3] = self.extended
        flag_byte[4:6] = self.max_hops
        flag_byte[6:8] = self.max_hops

        flag = flag_byte.tobytes()

        return flag

    def encode(self):
        """Encode the command into a byte string."""
        msg_flag = self.create_flag()

        cmd = self.from_address + self.to_address + msg_flag + self.cmd_bytes + self.extended_data

        return cmd

class PLMInsteonCommand(InsteonCommand):
    """
    Base class for commands sent over the PLM, basically attach '\x02\x62' infront of them
    and strip the from address.
    """

    def __init__(self, to_address, broadcast, group, ack, extended, max_hops, cmd1, cmd2, extended_data):
        super().__init__(self, b'\x02\x62', to_address, broadcast, group, ack, extended, max_hops, cmd1, cmd2, extended_data)

#Create a command where cmd1 and cmd2 are static, and our message flag is 0x0f
def _create_direct_static_standard_command(name, cmd1, cmd2):
    def __init__(self, address):
        PLMInsteonCommand.__init__(self, address, False, False, False, False, 3, cmd1, cmd2, b'')

    return type(name, (PLMInsteonCommand,), {'__init__' : __init__})

def _create_direct_variable_standard_command(name, cmd1):
    def __init__(self, address, cmd2):
        PLMInsteonCommand.__init__(self, address, False, False, False, False, 3, cmd1, cmd2, b'')

    return type(name, (PLMInsteonCommand,), {'__init__' : __init__})

#create an extended command where the data is supplied
def _create_direct_simple_extended_command(name, cmd1, cmd2):
    def __init__(self, address, extended_data):
        PLMInsteonCommand.__init__(self, address, False, False, False, True, 3, cmd1, cmd2, extended_data)

    return type(name, (PLMInsteonCommand,), {'__init__' : __init__})

def _create_interdevice_extended_command(name, cmd1, cmd2):
    def __init__(self, from_address, to_address, extended_data):
        InsteonCommand.__init__(self, from_address, to_address, False, False, False, True, 3, cmd1, cmd2, extended_data)

    return type(name, (InsteonCommand,), {'__init__' : __init__})

#The long wall of standard insteon commands, names should be self explinatory

#STANDARD COMMANDS
AssignToAllLinkGroup =  _create_direct_variable_standard_command('AssignToAllLinkGroup', b'\x01')
DeleteFromAllLinkGroup =  _create_direct_variable_standard_command('DeleteFromAllLinkGroup', b'\x02')
ProductDataRequest = _create_direct_static_standard_command('ProductDataRequest', b'\x03', b'\x00') 
FXUsernameRequest = _create_direct_static_standard_command('FXUsernameRequest', b'\x03', b'\x01') 
DeviceTextStringRequest = _create_direct_static_standard_command('DeviceTextStringRequest', b'\x03', b'\x02') 

EnterLinkingMode =  _create_direct_variable_standard_command('EnterLinkingMode', b'\x09')
EnterUnlinkingMode =  _create_direct_variable_standard_command('EnterUnlinkingMode', b'\x0A')

GetINSTEONVersion = _create_direct_static_standard_command('GetINSTEONVersion', b'\x0D', b'\x00') 

Ping = _create_direct_static_standard_command('Ping', b'\x0F', b'\x00') 
IDRequest = _create_direct_static_standard_command('IDRequest', b'\x10', b'\x00') 

TurnOn = _create_direct_static_standard_command('TurnOn', b'\x11', b'\x00') 
TurnOnLevel = _create_direct_variable_standard_command('TurnOnLevel', b'\x11') 

TurnOnFast= _create_direct_static_standard_command('TurnOnFast', b'\x12', b'\x00') 
TurnOnFastLevel = _create_direct_variable_standard_command('TurnOnFastLevel', b'\x12',) 

TurnOff = _create_direct_static_standard_command('TurnOff', b'\x13', b'\x00') 
TurnOffFast = _create_direct_static_standard_command('TurnOffFast', b'\x14', b'\x00')

#EXTENDED COMMANDS
SetDeviceTextString =  _create_direct_simple_extended_command('SetDeviceTextString', b'\x03', b'\x03')

TestInterdevice = _create_interdevice_extended_command('TestInterdevice',
    b'\x03', b'\x04')
