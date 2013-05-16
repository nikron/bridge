import struct
import logging

class EISPMessage():
    ISCP_START = b'ISCP'

    def __init__(self, command):
        self.command = command

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

        if b'MVL' in self.command:
            try:
                info['volume'] = int(self.command[4:6], 16)
            except ValueError:
                pass

        return info


    @classmethod
    def decode(cls, message):
        if message[0:4] != EISPMessage.ISCP_START:
            return None

        if message[4:8] != b'\x00\x00\x00\x10':
            return None

        start_of_cmd = message.find(b'!') + 1
        return cls(message[start_of_cmd:-1])

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

#
# Some of the possible commands
#

VOLUME_UP_COMMAND = b"MVLUP"
VOLUME_DOWN_COMMAND = b"MVLDOWN"
VOLUME_LEVEL_COMMAND = lambda x : b"MVL" + bytes(hex(x)[2:], "utf-8")
VOLUME_QUERY_COMMAND = b"MVLQSTN"
MUTE_TOGGLE_COMMAND  = b"AMTTG"
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

#
# Precomputed messages
#

VOLUME_QUERY = EISPMessage(VOLUME_QUERY_COMMAND).encode()
VOLUME_UP = EISPMessage(VOLUME_UP_COMMAND).encode()
VOLUME_DOWN = EISPMessage(VOLUME_DOWN_COMMAND).encode()
MUTE_TOGGLE = EISPMessage(MUTE_TOGGLE_COMMAND).encode()
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
SETSOURCEBDDVD = EISPMessage(INPUT_BDDVD_COMMAND).encode()
SETSOURCETVCD = EISPMessage(INPUT_TVCD_COMMAND).encode()


MODES = {
    b"00" : "Stereo",
    b"01" : "Direct",
    b"02" : "Surrond",
    b"03" : "Film",
    b"04" : "THX",
    b"05" : "Action",
    b"06" : "Musical",
    b"07" : "Mono Movie",
    b"08" : "Orchestra",
    b"09" : "Unplugged",
    b"0A" : "Studio-Mix",
    b"0B" : "TV Logic",
    b"0C" : "All Channel Stereo",
    b"0D" : "Theater - Dimensional",
    b"0E" : "Enhanced",
    b"0F" : "Mono",
    b"11" : "Pure Audio",
    b"12" : "Multiplex",
    b"13" : "Full Mono",
    b"14" : "Dolby Virtual",
    b"15" : "DTS Surrond Sensation",
    b"16" : "Audyessy DSX",
    b"1F" : "Whole House Mode",
    b"40" : "Straight Decode",
    b"41" : "Dolby EX/DTS ES",
    #b"41" : "Dolby EX 2", ensure which is correct
    b"42" : "THX Cinema",
    b"43" : "THX Surrond EX",
    b"44" : "THX Music",
    b"45" : "THX Games",
    b"50" : "THX U2",
    b"51" : "THX Music",
    b"52" : "THX U2 Games",
    b"80" : "PLII/PLIIx Movie",
    b"81" : "PLII/PLIIx Music",
    b"82" : "Neo:6 Cinema",
    b"83" : "Neo:6 Music",
    b"84" : "PLII/PLIIx THX Cinema",
    b"85" : "Neo:6 THX Cinema",
    b"86" : "PLII/PLIIx Game",
    b"87" : "Nueral Surrond",
    b"88" : "Nueral THX Surrond",
    b"89" : "PLII/PLIIx THX Games",
    b"8A" : "Neo:6 THX Games",
    b"8B" : "PLII/PLIIx THX Music",
    b"8C" : "Neo:6 THX Music",
    b"8D" : "Nueral THX Cinema",
    b"8E" : "Nueral THX Music",
    b"8F" : "Nueral THX Games",
    b"90" : "PLIIz Height",
    b"91" : "Neo:6 Cinema DTS Surround Sensation",
    b"92" : "Neo:6 Music DTS Surround Sensation",
    b"93" : "Neural Digital Music",
    b"94" : "PLIIz Height + THX Cinema",
    b"95" : "PLIIz Height + THX Music",
    b"96" : "PLIIz Height + THX Games",
    b"97" : "PLIIz Height + THX U2/S2 Cinema",
    b"98" : "PLIIz Height + THX U2/S2 Music",
    b"99" : "PLIIz Height + THX U2/S2 Games",
    b"9A" : "Neo:X Game",
    b"A0" : "PLIIx/PLII Movie + Audyssey DSX",
    b"A1" : "PLIIx/PLII Music + Audyssey DSX",
    b"A2" : "PLIIx/PLII Game + Audyssey DSX",
    b"A3" : "Neo:6 Cinema + Audyssey DSX",
    b"A4" : "Neo:6 Music + Audyssey DSX",
    b"A5" : "Neural Surround + Audyssey DSX",
    b"A6" : "Neural Digital Music + Audyssey DSX",
    b"A7" : "Dolby EX + Audyssey DSX"
}
