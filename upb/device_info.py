"""
Attempt to retrieve all information about a device
into a nice object from the device.
"""

from upb import pim, registers, UPBMessage
import logging

class UPBDeviceInfo():
    def __init__(self, uid, **kwargs):
        self.nid = None
        self.uid = uid
        self.npw = None
        self.ubop = None
        self.upbver = None
        self.mid = None
        self.pid = None
        self.fwver = None
        self.sernum = None
        self.nname = None
        self.rname = None
        self.dname = None

        for kwarg in kwargs:
            setattr(self, kwarg, kwargs[kwarg])

    def retrieve_information(self, ser, timeout = 4, retry = 4):
        saved_timeout = ser.getTimeout()
        ser.setTimeout(timeout)

        logging.debug("Retrieving first chunk for {0}.".format(self.uid))
        chunk = self._retrieve_chunk(ser, 0x00, retry)
        if chunk is not None:
            self.nid = chunk[0]
            self.uid = chunk[1]
            self.npw = chunk[2:4]
            self.ubop = chunk[4]
            self.upbver = chunk[5]
            self.mid = (chunk[6] << 8) + chunk[7]
            self.pid = (chunk[8] << 8) + chunk[9]
            self.fwver = (chunk[10] << 8) + chunk[11]
            self.sernum = (chunk[12] << 24) + (chunk[13] << 16) + (chunk[14] << 8) + chunk[15]

        logging.debug("Trying to get names for {0}.".format(self.uid))
        for name, (chunk, chunk_size) in zip(['nname', 'rname', 'dname'], [registers.NNAME, registers.RNAME, registers.DNAME]):
            chunk = self._retrieve_chunk(ser, chunk, retry, chunk_size)
            if chunk is not None:
                setattr(self, name, bytes(chunk))

        ser.setTimeout(saved_timeout)

    def _retrieve_chunk(self, ser, chunk_start, retry, chunk_size = 16):
        reg_des = registers.RegisterDescription((chunk_start, chunk_size))
        message = reg_des.create_get_registers(self.uid)

        tries = 0
        while tries < retry:
            pim.write_message(ser, message)

            pim_message = True
            while pim_message is not None:
                pim_message = pim.read(ser)
                if pim_message and pim_message.type == pim.PIMMessage.UPBMESSAGE:
                    message = UPBMessage.create_from_packet(pim_message.packet)
                    logging.debug(str(message))
                    if reg_des.is_report(message):
                        return message.arguments[1:]

            tries += 1
