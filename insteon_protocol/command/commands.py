"""
Create an Insteon command by calling the appriate object
with the correct information.
"""
from abc import ABCMeta, abstractmethod
import bitstring #maybe get rid of this depedance but it makes things easier

class Command():
    __metaclass__ = ABCMeta

    @abstractmethod
    def encode(self):
        pass

    @classmethod
    @abstractmethod
    def decode(cls, buf):
        pass



class InsteonCommand(Command):
    """Base class for all insteon commands."""

    def __init__(self, to_address, from_address, broadcast, group, ack, extended, cur_hops, max_hops, cmd1, cmd2, extended_data):
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
        flag_byte[4:6] = self.cur_hops
        flag_byte[6:8] = self.max_hops

        flag = flag_byte.tobytes()

        return flag

    def encode(self):
        """Encode the command into a byte string."""
        msg_flag = self.create_flag()

        cmd = self.from_address + self.to_address + msg_flag + self.cmd_bytes + self.extended_data

        return cmd

    @classmethod
    def decode(cls, buf):
        """Decode a byte string into an InsteonCommand."""

        fro = buf[0:3]
        to = buf[3:6]

        flag = bitstring.BitString(buf[6])
        broad = flag[0]
        group = flag[1]
        ack = flag[2]
        ext = flag[3]
        curh = flag[4:6]
        maxh = flag[6:8]

        cmd1 = buf[7]
        cmd2 = buf[8]

        ext = buf[9:]

        return cls(fro, to, broad, group, ack, ext, curh, maxh, cmd1, cmd2, ext)
