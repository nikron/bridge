import logging

def read(ser):
    """
    Read a response from the PIM.
    """
    reading = True
    timing_out = ser.getTimeout()
    buf = b''

    while reading:
        byte = ser.read()

        if byte == b'\r':
            reading = False
        elif timing_out is not None and byte == b'':
            return None

        buf += byte

    return PIMMessage(buf)

def write_message(ser, message):
    """
    Write a UPBMessage to a PIM.
    """
    ascii_packet = message.construct_ascii_packet()

    ser.write(b'\x14')
    ser.write(ascii_packet)
    ser.write(b'\r')

def execute_message(ser, message):
    tandem_messages = []
    tandem_reports = []
    successful = False
    waiting = True
    write_message(ser, message)

    while waiting:
        resp = read(ser)
        resp_type = resp.type
        logging.debug("Read in response of type {0}.".format(str(bytes([resp_type]))))

        if resp_type == PIMMessage.ACK:
            successful = True
            waiting = False
        elif resp_type == PIMMessage.NACK:
            waiting = False
        elif resp_type == PIMMessage.ERROR:
            waiting = False
        elif resp_type == PIMMessage.BUSY:
            waiting = False
        elif resp_type == PIMMessage.UPBMESSAGE:
            tandem_messages.append(resp.packet)
        elif resp_type == PIMMessage.REGISTER_REPORT:
            tandem_reports.append(resp.packet)

    return successful, tandem_messages, tandem_reports

class PIMMessage():
    UPBMESSAGE = ord(b'U')
    ACCEPT = ord(b'A')
    BUSY = ord(b'B')
    ERROR = ord(b'E')
    REGISTER_REPORT = ord(b'R')
    ACK = ord(b'K')
    NACK = ord(b'N')

    RESPONSE_TYPES = [ACCEPT, BUSY, ERROR, REGISTER_REPORT, ACK, NACK]

    def __init__(self, buf):
        self.validity_check(buf)
        self.type = buf[1]

        self.packet = buf[2:-1]

    @staticmethod
    def validity_check(buf):
        if buf[0] != 80:
            raise ValueError("PIM most likely not in message mode.")
