import binascii
import bitstring

from upb import mdid

class UPBMessage():
    GLOBAL_PACKET = 0
    DEFAULT_NETWORK_ID = 1
    DEFAULT_SOURCE_ID = 255
    DEFAULT_DESTINATION_ID = 1

    TRANSMIT_ONCE = 0
    TRANSMIT_TWICE = 1
    TRANSMIT_THRICE = 2
    TRANSMIT_QUAD = 3
    DEFAULT_TRANSMISSION_TIMES = TRANSMIT_QUAD

    REPEAT_Z = 0
    REPEAT_ONCE = 1
    REPEAT_TWICE = 2
    REPEAT_QUAD = 3
    DEFAULT_REPEAT = REPEAT_Z

    MDID = 0x00

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
        self.dirty = True
        self.ascii_packet = b''
        self.arguments = []

        for kwarg in kwargs:
            setattr(self, kwarg, kwargs[kwarg])

        self.length = 7 + len(self.arguments)

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
        return self.command() + [self.network_id, self.destination_id, self.source_id]

    def construct_message(self):
        return [self.MDID] + self.arguments

    def construct_checksum(self, body):
        j = sum(body)
        k = (1 << int.bit_length(j)) - j
        chk = bytes([k & 255]) #truncate to 8 bits
        return chk

    def construct_packet(self):
        hdr = self.construct_header()
        msg = self.construct_message()
        body = hdr + msg
        chk = self.construct_checksum(body)
        packet = bytes(body) + chk

        return binascii.hexlify(packet)

    def construct_ascii_packet(self):
        """
        Construct the packet to be sent to the PIM.  Note
        that the PIM takes in the packet in ASCII form, not the actual
        representation on the wire.
        """
        if not self.dirty:
            return self.ascii_packet
        else:
            self.ascii_packet = self.construct_packet()
            return self.ascii_packet

    def __str__(self):
        return str(vars(self))

    @classmethod
    def create_from_packet(cls, packet):
        st = packet.decode('ascii')
        ctl = bitstring.Bits(hex=st[0:4])

        net = int(st[4:6], 16)
        dest = int(st[6:8], 16)
        source = int(st[8:10], 16)
        _mdid = int(st[10:12], 16)
        link = ctl[0]
        repeat = ctl[1:3].uint
        ack = ctl[9]
        id_pul = ctl[10]
        ack_msg = ctl[11]
        trans_times = ctl[12:14].uint

        #info['len'] = ctl[3:8].uint

        args = []
        for i in range(12, len(st) - 2, 2):
            args.append(int(st[i:i+2], 16))

        upb_msg = cls(network_id = net, destination_id = dest, source_id = source,
                link = link, repeat = repeat, ack = ack, id_pulse = id_pul,
                ack_message = ack_msg, transmission_times = trans_times, arguments = args)

        upb_msg.MDID = _mdid

        return upb_msg

class UPBSimpleMessage(UPBMessage):
    """
    UPB message without any arguments.
    """
    def __init__(self, dest_id, **kwargs):
        super().__init__(destination_id = dest_id, **kwargs)

class UPBSimpleLinkMessage(UPBSimpleMessage):
    def __init__(self, dest_id, **kwargs):
        super().__init__(destination_id = dest_id, link = True, **kwargs)

class UPBSetRegisters(UPBMessage):
    MDID = mdid.SET_REGISTER_VALUE

    def __init__(self, reg, values, **kwargs):
        super().__init__(arguments = [reg] + values, **kwargs)

class UPBActivateLink(UPBSimpleLinkMessage):
    MDID = mdid.ACTIVATE_LINK

class UPBDeactivateLink(UPBSimpleLinkMessage):
    MDID = mdid.DEACTIVATE_LINK

class UPBGoToLevel(UPBMessage):
    """
    Going to a level on a specific channel DOES not work with
    links.
    """
    MDID = mdid.GOTO

    def __init__(self, dest_id, level, rate = None, channel = None, **kwargs):
        args = [level]
        if rate is not None:
            args.append(rate)

        super().__init__(destination_id = dest_id, arguments = args, **kwargs)
        self.level = level
        self.rate = rate
        self.channel = channel

        if not self.link and channel is not None:
            self.arguments.append(channel)
            self.length += 1

class UPBFadeStart(UPBMessage):
    """
    Going to a level on a specific channel DOES not work with
    links.
    """
    MDID = mdid.FADE_START

    def __init__(self, dest_id, rate = None, channel = None, **kwargs):
        args = []
        if rate is not None:
            args.append(rate)

        super().__init__(destination_id = dest_id, arguments = args, **kwargs)
        self.rate = rate
        self.channel = channel

        if not self.link and channel is not None:
            self.arguments.append(channel)
            self.length += 1

class UPBToggle(UPBMessage):
    MDID = mdid.TOGGLE

    def __init__(self, dest_id, times, rate=None, **kwargs):
        args = [times]
        if rate is not None:
            args.append(rate)

        super().__init__(destination_id = dest_id, arguments = args, **kwargs)
        self.toggle_times = times
        self.rate = rate

class UPBReportState(UPBSimpleMessage):
    """
    Report state must always be direct.
    """
    MDID = mdid.REPORT_STATE
