"""
Commands used to communicate to the insteon IM.
"""
from insteon_protocol.command.commands import InsteonCommand
from insteon_protocol.command.command_bytes import *

import bitstring

class IMInsteonCommand(InsteonCommand):
    """
    Base class for commands sent over the IM, basically attach '\x02\x62' infront of them
    and strip the from address.
    """

    def __init__(self, to_address, broadcast, group, ack, extended, cur_hops, max_hops, cmd1, cmd2, extended_data, okay=None):
        InsteonCommand.__init__(self, b'\x02\x62', to_address, broadcast, group, ack, extended, cur_hops, max_hops, cmd1, cmd2, extended_data)
        self.okay = okay

    @classmethod
    def decode(cls, buf):
        """
        Decode a byte string into an InsteonCommand. 
        NOTE: This ASSUMES the command comes from an IM (That it has either 06 or 15 appeneded
        to it.
        """

        to = buf[0:3]

        flag = bitstring.BitString(buf[3])
        broad = flag[0]
        group = flag[1]
        ack = flag[2]
        ext = flag[3]
        curh = flag[4:6]
        maxh = flag[6:8]

        cmd1 = buf[4:5]
        cmd2 = buf[5:6]

        ext = buf[6:-1]

        #go go duck typing
        if buf[-1:] == b'\x06':
            okay = True
        else:
            okay = False

        return cls(to, broad, group, ack, ext, curh, maxh, cmd1, cmd2, ext, okay)

#Create a command where cmd1 and cmd2 are static, and our message flag is 0x0f
def _create_direct_static_standard_command(name, cmd1, cmd2):
    def __init__(self, address):
        IMInsteonCommand.__init__(self, address, False, False, False, False, 3, 3, cmd1, cmd2, b'')

    return type(name, (IMInsteonCommand,), {'__init__' : __init__})

def _create_direct_variable_standard_command(name, cmd1):
    def __init__(self, address, cmd2):
        IMInsteonCommand.__init__(self, address, False, False, False, False, 3, 3, cmd1, cmd2, b'')

    return type(name, (IMInsteonCommand,), {'__init__' : __init__})

#create an extended command where the data is supplied
def _create_direct_simple_extended_command(name, cmd1, cmd2):
    def __init__(self, address, extended_data):
        IMInsteonCommand.__init__(self, address, False, False, False, True, 3, 3, cmd1, cmd2, extended_data)

    return type(name, (IMInsteonCommand,), {'__init__' : __init__})

def _create_interdevice_extended_command(name, cmd1, cmd2):
    def __init__(self, from_address, to_address, extended_data):
        InsteonCommand.__init__(self, from_address, to_address, False, False, False, True, 3, 3, cmd1, cmd2, extended_data)

    return type(name, (InsteonCommand,), {'__init__' : __init__})

#The long wall of standard insteon commands, names should be self explinatory

#STANDARD COMMANDS
AssignToAllLinkGroup =  _create_direct_variable_standard_command('AssignToAllLinkGroup', ASSIGNTOALLLINKGROUP.cmd1)
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

TurnOnFast= _create_direct_static_standard_command('TurnOnFast', TURNONFAST.cmd1, TURNONFAST.cmd2)
TurnOnFastLevel = _create_direct_variable_standard_command('TurnOnFastLevel', TURNONFAST.cmd1)

TurnOff = _create_direct_static_standard_command('TurnOff', TURNOFF.cmd1, TURNOFF.cmd2)
TurnOffFast = _create_direct_static_standard_command('TurnOffFast', b'\x14', b'\x00')

#EXTENDED COMMANDS
SetDeviceTextString =  _create_direct_simple_extended_command('SetDeviceTextString', b'\x03', b'\x03')

TestInterdevice = _create_interdevice_extended_command('TestInterdevice', b'\x03', b'\x04')
