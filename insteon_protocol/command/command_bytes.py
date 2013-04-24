"""
Constants for cmd1 and cmd2 bytes.
"""
from insteon_protocol.command.command_bytes_util import CMDS

ASSIGNTOALLLINKGROUP = CMDS(b'\x01')
DELETEFROMALLLINKGROUP = CMDS(b'\x02')
PRODUCTDATAREQUEST = CMDS(b'\x03', b'\x00')
FXUSERNAMEREQUEST = CMDS(b'\x03', b'\x01')
DEVICETEXTSTRINGREQUEST = CMDS(b'\x03', b'\x02')

ENTERLINKINGMODE = CMDS(b'\x09')
ENTERUNLINKINGMODE = CMDS(b'\x0A')
GETINSTEONVERSION = CMDS(b'\x0D', b'\x00')
PING = CMDS(b'\x0F', b'\x00')
IDREQUEST = CMDS(b'\x10', b'\x00')

TURNON = CMDS(b'\x11', b'\x00')
TURNONLEVEL = CMDS(b'\x11')

TURNONFAST = CMDS(b'\x12', b'\x00')
TURNOFF = CMDS(b'\x13', b'\x00')
TURNOFFFAST = CMDS(b'\x14', b'\x00')

LIGHTSTATUSREQUEST = CMDS(b'\x19', b'\x00', relative = True)
LIGHTSTATUSREQUESTLED = CMDS(b'\x19', b'\x01', relative = True)
