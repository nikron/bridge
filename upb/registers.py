from upb import UPBSetRegisters, UPBGetRegisters

NID = (0x00, 1)
UID = (0x01, 1)
NPW = (0x02, 2)
UPBOP = (0x03, 1)
UPBVER = (0x05, 1)
MID = (0x06, 2)
PID = (0x07, 2)
FWVER = (0x08, 2)
SERNUM = (0x0C, 4)
NNAME = (0x10, 16)
RNAME = (0x20, 16)
DNAME = (0x30, 16)

class RegisterDescription():
    def __init__(self, reg_tuple):
        self.start = reg_tuple[0]
        self.amount = reg_tuple[1]

    def create_set_registers(self, dest_id, _bytes):
        if len(_bytes) > self.amount:
            raise ValueError("Can only set up to {1} bytes.".format(self.amount))

        return UPBSetRegisters(dest_id, self.start, list(_bytes))

    def create_get_registers(self, dest_id):
        return UPBGetRegisters(dest_id, self.start, self.amount)

    def is_report(self, message):
        try:
            if message.arguments[0] == self.start and  len(message.arguments) -1 == self.amount:
                return True

        except IndexError:
            return False

        return False

    @staticmethod
    def make_string(message):
        return bytes(message.arguments[1:]).decode().strip()

