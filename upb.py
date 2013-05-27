import binascii
import bitstring

class UPBMessage():
    GLOBAL_PACKET = 0
    DEFAULT_NETWORK_ID = 1
    DEFAULT_SOURCE_ID = 255
    DEFAULT_DESTINATION_ID = 1

    TRANSMIT_ONCE = '0b00'
    TRANSMIT_TWICE = '0b01'
    TRANSMIT_THRICE = '0b10'
    TRANSMIT_QUAD = '0b11'
    DEFAULT_TRANSMISSION_TIMES = TRANSMIT_QUAD

    REPEAT_Z = '0b00'
    REPEAT_ONCE = '0b01'
    REPEAT_TWICE = '0b10'
    REPEAT_QUAD = '0b11'
    DEFAULT_REPEAT = REPEAT_Z

    def __init__(self, **kwargs):
        self.network_id = UPBMessage.DEFAULT_NETWORK_ID
        self.destination_id = UPBMessage.DEFAULT_DESTINATION_ID
        self.link = False
        self.source_id = UPBMessage.DEFAULT_SOURCE_ID
        self.transmission_times = UPBMessage.DEFAULT_TRANSMISSION_TIMES
        self.ack = True
        self.id_pulse = False
        self.ack_msg = False
        self.repeat = UPBMessage.DEFAULT_REPEAT
        self.reply_repeat = False
        self.length = 7
        self.dirty = True
        self.ascii_packet = b''

    def command(self):
        CTL = bitstring.BitArray(16)

        CTL[0] = self.link
        CTL[1:3] = self.repeat

        j = 3 + (5 - int.bit_length(self.length))
        CTL[j:8] = bin(self.length)

        CTL[9] = self.ack_msg
        CTL[10] = self.id_pulse
        CTL[11] = self.ack
        CTL[12:14] = self.transmission_times
        CTL[14] = False
        CTL[15] = False

        return [CTL[0:8].uint, CTL[8:16].uint]

    def construct_header(self):
        return self.command() + \
                [self.network_id, \
                self.destination_id, \
                self.source_id]

    def construct_message(self):
        raise NotImplementedError

    def construct_checksum(self, body):
        j = sum(body)
        k = (1 << int.bit_length(j)) - j
        #chk = bytes([bitstring.Bits(uint=k, length=8).uint])
        #chk = int.to_bytes(k, 1, 'little')
        chk = bytes.fromhex(hex(k)[-2:])
        return chk

    def construct_packet(self):
        hdr = self.construct_header()
        msg = self.construct_message()
        body = hdr + msg
        chk = self.construct_checksum(body)
        packet = bytes(body) + chk

        return binascii.hexlify(packet)

    def construct_ascii_packet(self):
        if not self.dirty:
            return self.ascii_packet
        else:
            self.ascii_packet = self.construct_packet()
            return self.ascii_packet

#all the messages without agruements
def UPBSimpleLinkMessage(name, command):
    def __init__(self, dest_id):
        UPBMessage.__init__(self)
        self.destination_id = dest_id
        self.link = True

    class_dict = {}
    class_dict['MDID'] = command
    class_dict['__init__'] = __init__
    class_dict['construct_message'] = lambda self : [self.MDID]

    return type(name, (UPBMessage,), class_dict)

#UPBNull = UPBNoArguementMessage('UPBNull', 0x00)
#
#UPBWriteProtect = UPBNoArguementMessage('UPBWriteProtect', 0x02)
#
#UPBStopSetup = UPBNoArguementMessage('UPBStopSetup', 0x04)
#
#UPBGetSetupTime = UPBNoArguementMessage('UPBGetSetupTime', 0x05)
#
#UPBAutoAddress = UPBNoArguementMessage('UPBAutoAddress', 0x06)
#
#UPBGetDeviceStatus = UPBNoArguementMessage('UPBGetDeviceStatus', 0x07)

UPBActivateLink = UPBSimpleLinkMessage('UPBActivateLink', 0x20)
UPBDeactivateLink = UPBSimpleLinkMessage('UPBDeactivateLink', 0x21)

class UPBGoToLevel(UPBMessage):
    MDID = 0x22

    def __init__(self, dest_id, level, link, rate = None, channel = None):
        UPBMessage.__init__(self)
        self.destination_id = dest_id
        self.level = level
        self.link = link
        self.rate = rate
        self.channel = channel
        self.length += 1

        if self.rate is not None:
            self.length += 1

            if not self.link and channel is not None:
                self.length += 1

    def construct_message(self):
        msg = [self.MDID, self.level]
        if self.rate is not None:
            msg += [self.rate]

            if not self.link and self.channel is not None:
                msg += [self.channel]
        return msg

class UPBReportState(UPBMessage):
    def __init__(self, dest_id):
        UPBMessage.__init__(self)
        self.destination_id = dest_id
        self.link = False #report state will always be direct

    def construct_message(self):
        msg = [0x30]

        return msg

class UPBControlFadeStart(UPBMessage):
    def __init__(self, level, rate = None, channel = None, **kwargs):
        UPBMessage.__init__(self, **kwargs)
        self.level = level
        self.rate = rate
        self.channel = channel

        if self.rate is not None:
            self.length += 1

            if not self.link and channel is not None:
                self.length += 1

    def construct_message(self):
        msg = [0x23]
        if self.rate is not None:
            msg += [self.rate]

            if not self.link and self.channel is not None:
                msg += [self.channel]
        return msg

class UPBToggle(UPBMessage):
    def __init__(self, dest_id, link, times, rate=None):
        UPBMessage.__init__(self)
        self.destination_id = dest_id
        self.link = link
        self.toggle_times = times
        self.rate = rate
        self.length += 1 # always will have toggle times

        if rate is not None:
            self.length += 1

    def construct_message(self):
        msg = [0x27]

        msg += [self.toggle_times]

        if self.rate is not None:
            msg += [self.rate]

        return msg


class UPBSetRegisters(UPBMessage):
    def __init__(self, reg, values, **kwargs):
        UPBMessage.__init__(self, **kwargs)
        self.reg = reg
        self.values = values
        self.length += 1 + len(values)

    def construct_message(self):
        return [0x11, self.reg] + self.values

def create_upb_set_register(name, register, func):
    def __init__(self, data, **kwargs):
        UPBSetRegisters.__init__(self, register, func(data), **kwargs)

    return type(name, (UPBSetRegisters,), {'__init__' : __init__})

strtoint = lambda string : list(string.encode())

def inttopwd(x):
    y = bitstring.BitArray(hex(x))
    return [y[0:2].int, y[2,4].int]

UPBSetNetworkName = create_upb_set_register('UPBSetNetworkName', 0x10, strtoint)
UPBSetRoomName = create_upb_set_register('UPBSetRoomName', 0x20, strtoint)
UPBSetDeviceName = create_upb_set_register('UPBSetDeviceName', 0x30, strtoint)
UPBSetPassword = create_upb_set_register('UPBSetPassword', 0x02, inttopwd)


def info_from_packet(packet):
    info = {}

    st = packet.decode('ascii')
    ctl = bitstring.Bits(hex=st[0:4])

    info['ctl'] = ctl
    info['network id'] = int(st[4:6], 16)
    info['destination id'] = int(st[6:8], 16)
    info['source id'] = int(st[8:10], 16)
    info['message id'] = int(st[10:12], 16)
    info['link'] = ctl[0]
    info['repeats'] = ctl[1:3].uint
    info['len'] = ctl[3:8].uint
    info['ack'] = ctl[9]
    info['id pulse'] = ctl[10]
    info['ack message'] = ctl[11]
    info['transmission times'] = ctl[12:14].uint

    arg_list = []
    for i in range(12, len(st) - 2, 2):
        arg_list.append(int(st[i:i+2], 16))

    info['message args'] = arg_list

    return info
