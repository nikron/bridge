def read(serial):
    """
    Read a response from the PIM.
    """
    reading = True
    buf = b''

    while reading:
        byte = serial.read()
        if byte == b'\r':
            reading = False
        buf += byte

    return PIMMessage(buf)

def write_message(serial, message):
    """
    Write a UPBMessage to a PIM.
    """
    ascii_packet = message.construct_ascii_packet()

    serial.write(b'\x14')
    serial.write(ascii_packet)
    serial.write(b'\r')

def execute_message(serial, message):
    tandem_messages = []
    tandem_reports = []
    successful = False
    waiting = True
    write_message(serial, message)

    while waiting:
        resp = read(serial)
        resp_type =  resp.type

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
        else:
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

