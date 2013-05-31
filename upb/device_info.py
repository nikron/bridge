"""
Attempt to retrieve all information about a device
into a nice object from the device.
"""

from upb import pim, registers, UPBMessage
import logging

class UPBDeviceInfo():
    def __init__(self, **kwargs):
        self.nid = None
        self.uid = None
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

    @classmethod
    def retrieve_information(cls, ser, device_id, timeout = 4, retry = 4):
        saved_timeout = ser.getTimeout()
        ser.setTimeout(timeout)

        logging.debug("Retrieving first chunk for {0}.".format(str(device_id)))
        chunk = cls._retrieve_chunk(ser, device_id, 0x00, retry)
        if chunk is None:
            ser.setTimeout(saved_timeout)
            return None

        device_info = cls()
        device_info.nid = chunk[0]
        device_info.uid = chunk[1]
        device_info.npw = chunk[2:4]
        device_info.ubop = chunk[4]
        device_info.upbver = chunk[5]
        device_info.mid = (chunk[6] << 8) + chunk[7]
        device_info.pid = (chunk[8] << 8) + chunk[9]
        device_info.fwver = (chunk[10] << 8) + chunk[11]
        device_info.sernum = (chunk[12] << 24) + (chunk[13] << 16) + (chunk[14] << 8) + chunk[15]

        logging.debug("Trying to get names for {0}.".format(str(device_id)))
        for name, (chunk, chunk_size) in zip(['nname', 'rname', 'dname'], [registers.NNAME, registers.RNAME, registers.DNAME]):
            chunk = cls._retrieve_chunk(ser, device_id, chunk, retry, chunk_size)
            if chunk is None:
                ser.setTimeout(saved_timeout)
                return None
            else:
                setattr(device_info, name, bytes(chunk))

        ser.setTimeout(saved_timeout)

        return device_info

    @staticmethod
    def _retrieve_chunk(ser, device_id, chunk_start, retry, chunk_size = 16):
        reg_des = registers.RegisterDescription((chunk_start, chunk_size))
        message = reg_des.create_get_registers(device_id)

        tries = 0
        while tries < retry:
            success, _, _  = pim.execute_message(ser, message)
            if not success:
                return None

            pim_message = True
            while pim_message is not None:
                pim_message = pim.read(ser)
                if pim_message and pim_message.type == pim.PIMMessage.UPBMESSAGE:
                    message = UPBMessage.create_from_packet(pim_message.packet)
                    logging.debug(str(message))
                    if reg_des.is_report(message):
                        return message.arguments[1:]

            tries += 1
