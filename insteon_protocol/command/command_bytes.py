"""
Constants for cmd1 and cmd2 bytes.
"""

#__all__ = ['ASSIGNTOALLLINKGROUP', 'TURNONFAST', 'TURNOFF']

class CMDS():
    def __init__(self, cmd1, cmd2=None):
        self.cmd1 = cmd1
        self.cmd2 = cmd2
        if self.cmd2:
            self.both = cmd1 + cmd2
        else:
            self.both = cmd1

    def __eq__(self, other):
        return self.both == other.both

    def __cmp__(self, other):
        return self.both.__cmp__(other.__both__)

    def __hash__(self):
        return hash(self.both)

ASSIGNTOALLLINKGROUP = CMDS(b'\x01')
TURNONFAST = CMDS(b'\x12', b'\x00')
TURNOFF = CMDS(b'\x13', b'\x00')

