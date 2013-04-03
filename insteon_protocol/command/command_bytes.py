"""
Constants for cmd1 and cmd2 bytes.
"""
from insteon_protocol.command.command_bytes_util import CMDS

#__all__ = ['ASSIGNTOALLLINKGROUP', 'TURNONFAST', 'TURNOFF']

ASSIGNTOALLLINKGROUP = CMDS(b'\x01')
DELETEFROMALLLINKGROUP = CMDS(b'\x02')
PRODUCTDATAREQUEST = CMDS(b'\x03', b'\x00')
TURNONFAST = CMDS(b'\x12', b'\x00')
TURNOFF = CMDS(b'\x13', b'\x00')

