import struct
import logging

class EISPMessage():
    VOLUME_UP = b"MVLUP"
    VOLUME_DOWN = b"MVLDOWN"
    VOLUME_LEVEL = lambda x : b"MVL" + bytes(hex(x)[2:], "utf-8")
    VOLUME_QUERY = b"MVLQSTN"
    MUTE_TOGGLE  = b"AMTTG"
    MENU = b'OSDMENU'
    UP = b'OSDUP'
    DOWN = b'OSDDOWN'
    LEFT = b'OSDLEFT'
    RIGHT = b'OSDRIGHT'
    EXIT = b'OSDEXIT'
    ENTER = b'OSDENTER'
    AUDIO = b'OSDAUDIO'
    VIDEO = b'OSDVIDEO'
    HOME = b'OSDHOME'
    INPUT_BDDVD = b'SLI10'
    INPUT_TVCD = b'SLI23'

    def __init__(self, command):
        self.command = command

    def encode(self):
        packet = b''
        buf = []

        buf.append(b'ISCP')
        buf.append(b'\x00\x00\x00\x10') #header size

        total_size = bytes([len(self.command) + 19]) #don't understand magic
        buf.append(b'\x00\x00\x00' + total_size)

        buf.append(b'\x01') #version
        buf.append(b'\x00\x00\x00') #reserved
        buf.append(b'!') #seperator
        buf.append(b'1') #receiver

        buf.append(self.command)
        buf.append(b'\r') #end (why does it need EOF and size)

        packet = packet.join(buf)

        return packet

    def __bytes__(self):
        return self.encode()

VolumeQuery = EISPMessage(EISPMessage.VOLUME_QUERY)
VolumeUp = EISPMessage(EISPMessage.VOLUME_UP)
VolumeDown = EISPMessage(EISPMessage.VOLUME_DOWN)
MuteToggle = EISPMessage(EISPMessage.MUTE_TOGGLE)
Menu = EISPMessage(EISPMessage.MENU)
Up = EISPMessage(EISPMessage.UP)
Right = EISPMessage(EISPMessage.RIGHT)
Left = EISPMessage(EISPMessage.LEFT)
Down = EISPMessage(EISPMessage.DOWN)
Enter = EISPMessage(EISPMessage.ENTER)
Exit = EISPMessage(EISPMessage.EXIT)
Video = EISPMessage(EISPMessage.VIDEO)
Audio = EISPMessage(EISPMessage.AUDIO)
Home = EISPMessage(EISPMessage.HOME)
SetSourceBDDVD = EISPMessage(EISPMessage.INPUT_BDDVD)
SetSourceTVCD = EISPMessage(EISPMessage.INPUT_TVCD)


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
    b"41" : "Dolby EX 2",
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

def read_info(socket):
    packet = socket.recv(4) #read b'ISCP' hopefully
    buf = socket.recv(12) #get the rest of the header
    packet = packet + buf

    if len(buf) != 12:
        logging.error("header not 12")

    body_size = struct.unpack(">L", buf[4:8])[0]
    body = socket.recv(body_size)
    packet = packet + body

    logging.debug("Read {0} from EISP connection.".format(str(packet)))
    return deconstruct_packet(packet)


def deconstruct_packet(packet):
    #print(str(len(packet)) + " bytes: " + repr(packet))
    if packet[0:4] != b'ISCP':
        return None
    if packet[4:8] != b'\x00\x00\x00\x10':
        pass

    body = struct.unpack(">L", packet[8:12])[0]
    #print("body: " + repr(packet[16:16+body]))
    cmd = packet[18:21]

    info = {}
    if cmd == b'MVL':
        try:
            info["mvl"] = int(packet[21:23], 16)
        except ValueError:
            pass

    if cmd == b'LMD':
        info["lmd"] = MODES[packet[21:23]]

    return info
