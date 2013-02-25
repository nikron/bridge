from abc import ABCMeta, abstractmethod
import bitstring #maybe get rid of this depedance but it makes things easier
import logging

class Command():
    __metaclass__ = ABCMeta

    @abstractmethod
    def encode(self):
        pass

class InsteonCommand(Command):
    def __init__(self, address, broadcast, group, ack, extended, max_hops, cmd1, cmd2):

        flag_byte = bitstring.BitString(8)
        flag_byte[0] = broadcast
        flag_byte[1] = group
        flag_byte[2] = ack
        flag_byte[3] = extended
        flag_byte[4:6] = max_hops
        flag_byte[6:8] = max_hops

        self.msg_flags = flag_byte.tobytes()

        self.cmd_bytes = cmd1 + cmd2

        self.cmd = b'\x02\x62' + address + self.msg_flags + self.cmd_bytes
    
    def encode(self):
        return self.cmd
        
#Create a command where cmd1 and cmd2 are static, and our message flag is 0x0f
def _create_direct_static_standard_command(name, cmd1, cmd2):
    def __init__(self, address):
        InsteonCommand.__init__(self, address, False, False, False, False, 3, cmd1, cmd2)

    return type(name, (InsteonCommand,), {'__init__' : __init__})

def _create_direct_variable_standard_command(name, cmd1):
    def __init__(self, address, cmd2):
        InsteonCommand.__init__(self, address, False, False, False, False, 3, cmd1, cmd2)

    return type(name, (InsteonCommand,), {'__init__' : __init__})


#The long wall of standard insteon commands, names should be self explinatory
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
TurnOnFast = _create_direct_static_standard_command('TurnOnFast', b'\x12', b'\x00') 
TurnOff = _create_direct_static_standard_command('TurnOff', b'\x13', b'\x00') 
