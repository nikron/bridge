from abc import ABCMeta, abstractmethod, abstractclassmethod

class EISPMessage():
    ISCP_START = b'ISCP'

    def __init__(self, encoded_command):
        self.command = encoded_command

    def encode(self):
        message = b''
        buf = []

        buf.append(EISPMessage.ISCP_START)
        buf.append(b'\x00\x00\x00\x10') #header size

        total_size = bytes([len(self.command) + 19]) #19 is size of rest of message besides command
        buf.append(b'\x00\x00\x00' + total_size)

        buf.append(b'\x01') #version
        buf.append(b'\x00\x00\x00') #reserved
        buf.append(b'!') #seperator
        buf.append(b'1') #receiver

        buf.append(self.command)
        buf.append(b'\r') #end (why does it need EOF and size)

        message = message.join(buf)

        return message

    def decipher(self):
        """
        Tries to split a command into useful parts.
        """
        info = {'command' : self.command}

        info['deciphered'] = COMMANDS.decode_command(self.command)

        return info

    @classmethod
    def decode(cls, message):
        if message[0:4] != EISPMessage.ISCP_START:
            return None

        if message[4:8] != b'\x00\x00\x00\x10':
            return None

        start_of_cmd = message.find(b'!') + 2 #skip past the product type, should always be 1
        end_of_cmd = message.find(b'\x1a')
        return cls(message[start_of_cmd:end_of_cmd])

def read_message(socket):
    """
    Read a EISP message from a socket, waits on reads.

    :param socket: Socket to read from.
    :type socket: socket

    :return: :class:`EISPMessage` with command property set to returned command
    :rtype: :class:`EISPMessage`
    """

    packet = socket.recv(4) #read b'ISCP' hopefully
    buf = socket.recv(12) #get the rest of the header
    packet = packet + buf

    if len(buf) != 12:
        logging.error("Could not read the entire EISP header.")
        return None

    body_size = struct.unpack(">L", buf[4:8])[0]
    body = socket.recv(body_size)
    packet = packet + body

    logging.debug("Read {0} from EISP connection.".format(str(packet)))

    return EISPMessage.decode(packet)

class TwoWayDict(dict):
    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        dict.__setitem__(self, value, key)

class Command():
    def __init__(self, value, pretty, queryable = True, **kwargs):
        self.value = value
        self.pretty = pretty
        self.keywords = TwoWayDict()
        if queryable:
            self.keywords['query'] = b'QSTN'

        for decoded in kwargs:
            self.keywords[decoded] = kwargs[decoded]

    def encode(self, arg):
        return self.value + self.keywords[arg]

    def decode(self, arg):
        return self.keywords[arg]

class BinaryCommand(Command):
    def encode(self, arg):
        if arg is True:
            return self.value + b'01'
        elif arg is False:
            return self.value + b'00'
        else:
            return super().encode(arg)

    def decode(self, arg):
        if arg == b'01':
            return True
        elif arg == b'00':
            return False
        else:
            return super().encode(arg)

class IntCommand(Command):
    def encode(self, arg):
        if type(arg) is int:
            return self.value + format(arg, '02x').encode()
        else:
            return super().encode(arg)

    def decode(self, arg):
        try:
            return int(arg, 16)
        except ValueError:
            return super().encode(arg)

class Commands():
    def __init__(self):
        self.values = {}
        self.pretties = {}

    def add(self, command):
        self.values[command.value] = command
        self.pretties[command.pretty] = command

    def get(self, pretty):
        return self.pretties[pretty]

    def decode_command(self, encoded_command):
        command = self.values[encoded_command[0:3]]
        return command.pretty, command.decode(command[3:])

    def __getitem__(self, item):
        return self.get(item)

COMMANDS = Commands()
COMMANDS.add(BinaryCommand(b'AMT', 'mute', toggle = b'TG'))
COMMANDS.add(IntCommand(b'MVL', 'volume', up = b'UP', down = b'DOWN'))

#
# Some of the possible commands
#

VOLUME_UP_COMMAND = b'MVLUP'
VOLUME_DOWN_COMMAND = b'MVLDOWN'
VOLUME_LEVEL_COMMAND = lambda x : b'MVL' + bytes([x])
VOLUME_QUERY_COMMAND = b'MVLQSTN'
MENU_COMMAND = b'OSDMENU'
UP_COMMAND = b'OSDUP'
DOWN_COMMAND = b'OSDDOWN'
LEFT_COMMAND = b'OSDLEFT'
RIGHT_COMMAND = b'OSDRIGHT'
EXIT_COMMAND = b'OSDEXIT'
ENTER_COMMAND = b'OSDENTER'
AUDIO_COMMAND = b'OSDAUDIO'
VIDEO_COMMAND = b'OSDVIDEO'
HOME_COMMAND = b'OSDHOME'
INPUT_BDDVD_COMMAND = b'SLI10'
INPUT_TVCD_COMMAND = b'SLI23'
INPUT_QUERY_COMMAND = b'SLIQSTN'

#
# Precomputed messages
#

VOLUME_QUERY = EISPMessage(COMMANDS['volume'].encode('query')).encode()
VOLUME_UP = EISPMessage(COMMANDS['volume'].encode('up')).encode()
VOLUME_DOWN = EISPMessage(COMMANDS['volume'].encode('down')).encode()
MUTE_ON = EISPMessage(COMMANDS['mute'].encode(True)).encode()
MUTE_OFF = EISPMessage(COMMANDS['mute'].encode(False)).encode()
MUTE_TOGGLE = EISPMessage(COMMANDS['mute'].encode('toggle')).encode()
MUTE_QUERY = EISPMessage(COMMANDS['mute'].encode('query')).encode()
MENU = EISPMessage(MENU_COMMAND).encode()
UP = EISPMessage(UP_COMMAND).encode()
RIGHT = EISPMessage(RIGHT_COMMAND).encode()
LEFT = EISPMessage(LEFT_COMMAND).encode()
DOWN = EISPMessage(DOWN_COMMAND).encode()
ENTER = EISPMessage(ENTER_COMMAND).encode()
EXIT = EISPMessage(EXIT_COMMAND).encode()
VIDEO = EISPMessage(VIDEO_COMMAND).encode()
AUDIO = EISPMessage(AUDIO_COMMAND).encode()
HOME = EISPMessage(HOME_COMMAND).encode()
SET_INPUT_BDDVD = EISPMessage(INPUT_BDDVD_COMMAND).encode()
SET_INPUT_TVCD = EISPMessage(INPUT_TVCD_COMMAND).encode()
INPUT_QUERY = EISPMessage(INPUT_QUERY_COMMAND).encode()

MODES = TwoWayDict()
MODES[b'00'] = 'Stereo'
MODES[b'01'] = 'Direct'
MODES[b'02'] = 'Surrond'
MODES[b'03'] = 'Film'
MODES[b'04'] = 'THX'
MODES[b'05'] = 'Action'
MODES[b'06'] = 'Musical'
MODES[b'07'] = 'Mono Movie'
MODES[b'08'] = 'Orchestra'
MODES[b'09'] = 'Unplugged'
MODES[b'0A'] = 'Studio-Mix'
MODES[b'0B'] = 'TV Logic'
MODES[b'0C'] = 'All Channel Stereo'
MODES[b'0D'] = 'Theater - Dimensional'
MODES[b'0E'] = 'Enhanced'
MODES[b'0F'] = 'Mono'
MODES[b'11'] = 'Pure Audio'
MODES[b'12'] = 'Multiplex'
MODES[b'13'] = 'Full Mono'
MODES[b'14'] = 'Dolby Virtual'
MODES[b'15'] = 'DTS Surrond Sensation'
MODES[b'16'] = 'Audyessy DSX'
MODES[b'1F'] = 'Whole House Mode'
MODES[b'40'] = 'Straight Decode'
MODES[b'41'] = 'Dolby EX/DTS ES'
MODES[b'42'] = 'THX Cinema'
MODES[b'43'] = 'THX Surrond EX'
MODES[b'44'] = 'THX Music'
MODES[b'45'] = 'THX Games'
MODES[b'50'] = 'THX U2'
MODES[b'51'] = 'THX Music'
MODES[b'52'] = 'THX U2 Games'
MODES[b'80'] = 'PLII/PLIIx Movie'
MODES[b'81'] = 'PLII/PLIIx Music'
MODES[b'82'] = 'Neo:6 Cinema'
MODES[b'83'] = 'Neo:6 Music'
MODES[b'84'] = 'PLII/PLIIx THX Cinema'
MODES[b'85'] = 'Neo:6 THX Cinema'
MODES[b'86'] = 'PLII/PLIIx Game'
MODES[b'87'] = 'Nueral Surrond'
MODES[b'88'] = 'Nueral THX Surrond'
MODES[b'89'] = 'PLII/PLIIx THX Games'
MODES[b'8A'] = 'Neo:6 THX Games'
MODES[b'8B'] = 'PLII/PLIIx THX Music'
MODES[b'8C'] = 'Neo:6 THX Music'
MODES[b'8D'] = 'Nueral THX Cinema'
MODES[b'8E'] = 'Nueral THX Music'
MODES[b'8F'] = 'Nueral THX Games'
MODES[b'90'] = 'PLIIz Height'
MODES[b'91'] = 'Neo:6 Cinema DTS Surround Sensation'
MODES[b'92'] = 'Neo:6 Music DTS Surround Sensation'
MODES[b'93'] = 'Neural Digital Music'
MODES[b'94'] = 'PLIIz Height + THX Cinema'
MODES[b'95'] = 'PLIIz Height + THX Music'
MODES[b'96'] = 'PLIIz Height + THX Games'
MODES[b'97'] = 'PLIIz Height + THX U2/S2 Cinema'
MODES[b'98'] = 'PLIIz Height + THX U2/S2 Music'
MODES[b'99'] = 'PLIIz Height + THX U2/S2 Games'
MODES[b'9A'] = 'Neo:X Game'
MODES[b'A0'] = 'PLIIx/PLII Movie + Audyssey DSX'
MODES[b'A1'] = 'PLIIx/PLII Music + Audyssey DSX'
MODES[b'A2'] = 'PLIIx/PLII Game + Audyssey DSX'
MODES[b'A3'] = 'Neo:6 Cinema + Audyssey DSX'
MODES[b'A4'] = 'Neo:6 Music + Audyssey DSX'
MODES[b'A5'] = 'Neural Surround + Audyssey DSX'
MODES[b'A6'] = 'Neural Digital Music + Audyssey DSX'
MODES[b'A7'] = 'Dolby EX + Audyssey DSX'


#MODES[b'41' : 'Dolby EX 2', ensure which is correct
