"""
Commands used to communicate to the insteon IM.
"""
from insteon.command.commands import InsteonCommand
from insteon.command.command_bytes import *

import bitstring

class IMInsteonCommand(InsteonCommand):
    """
    Base class for commands sent over the IM, basically attach '\x02\x62' infront of them
    and strip the from address.
    """
    __relative__ = False #Is the response to this command relative to this one?

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
        buf = buf[2:] #strip the start of command and command type

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

        if buf[-1:] == b'\x06':
            okay = True
        else:
            okay = False

        return cls(to, broad, group, ack, ext, curh, maxh, cmd1, cmd2, ext, okay)

    @classmethod
    def is_relative(cls):
        """
        Whether the response to this IM command is relative to this one.
        """
        return cls.__relative__


def create_standard_im_command(name, cmd_bytes):
    """
    Create an InsteonIMCommand object out of a command bytes object.
    """
    _dict = {}
    if not cmd_bytes.is_variable():
        def __init__(self, address):
            IMInsteonCommand.__init__(self, address, False, False, False, False, 3, 3, cmd_bytes.cmd1, cmd_bytes.cmd2, b'')
        _dict['__init__'] = __init__
    else:
        def __init__(self, address, cmd2):
            IMInsteonCommand.__init__(self, address, False, False, False, False, 3, 3, cmd_bytes.cmd1, cmd2, b'')
        _dict['__init__'] = __init__

    _dict['__relative__'] = cmd_bytes.is_relative()

    return type(name, (IMInsteonCommand,), _dict)

#The long wall of standard insteon commands, names should be self explinatory

#STANDARD COMMANDS
AssignToAllLinkGroup =  create_standard_im_command('AssignToAllLinkGroup', ASSIGNTOALLLINKGROUP)
DeleteFromAllLinkGroup =  create_standard_im_command('DeleteFromAllLinkGroup', DELETEFROMALLLINKGROUP)
ProductDataRequest = create_standard_im_command('ProductDataRequest', PRODUCTDATAREQUEST)
FXUsernameRequest = create_standard_im_command('FXUsernameRequest', FXUSERNAMEREQUEST)
DeviceTextStringRequest = create_standard_im_command('DeviceTextStringRequest', DEVICETEXTSTRINGREQUEST)

EnterLinkingMode =  create_standard_im_command('EnterLinkingMode', ENTERLINKINGMODE)
EnterUnlinkingMode =  create_standard_im_command('EnterUnlinkingMode', ENTERUNLINKINGMODE)

GetINSTEONVersion = create_standard_im_command('GetINSTEONVersion', GETINSTEONVERSION)

Ping = create_standard_im_command('Ping', PING)
IDRequest = create_standard_im_command('IDRequest', IDREQUEST)

TurnOn = create_standard_im_command('TurnOn',TURNON)
TurnOnLevel = create_standard_im_command('TurnOnLevel', TURNONLEVEL)

TurnOnFast= create_standard_im_command('TurnOnFast', TURNONFAST)
TurnOnFastLevel = create_standard_im_command('TurnOnFastLevel', TURNONFAST)

TurnOff = create_standard_im_command('TurnOff', TURNOFF)
TurnOffFast = create_standard_im_command('TurnOffFast', TURNOFFFAST)

LightStatusRequest = create_standard_im_command('LightStatusRequest', LIGHTSTATUSREQUEST)
