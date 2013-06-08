"""
Known MDID's according to pdf document on PCS website.
"""

#
# UPB Core Set
#

NULL = 0x00
WRITE_ENABLE = 0x01
WRITE_PROTECT = 0x02
START_SETUP_MODE = 0x03
STOP_SETUP_MODE = 0x04
GET_SETUP_TIME = 0x05
AUTO_ADDRESS = 0x06
GET_DEVICE_STATUS = 0x07
SET_DEVICE_CONTROL = 0x08

#
# 0x09 - 0x0A Unused
#

ADD_LINK = 0x0B
DELETE_LINK = 0x0C
TRANSMIT_THIS_MESSAGE = 0x0D
DEVICE_RESET = 0x0E
GET_DEVICE_SIGNATURE = 0x0F
GET_REGISTER_VALUE = 0x10
SET_REGISTER_VALUE = 0x11

#
# 0x12 - 0x1F Unused
#

#
# The Device Control Set
#

ACTIVATE_LINK = 0x20
DEACTIVATE_LINK = 0x21
GOTO = 0x22
FADE_START = 0x23
FADE_STOP = 0x24
BLINK = 0x25
INDICATE = 0x26
TOGGLE = 0x27

#
# 0x28 - 0x2F Unused
#

REPORT_STATE = 0x30
STORE_STATE = 0x31

#
# 0x32 - 0x3F Unused
#

#
# UPB Core Report Set
#

ACKNOWLEDGEMENT = 0x80

#
# 0x81 - 0x84 Unused
#

SETUP_TIME = 0x85
DEVICE_STATE = 0x86
DEVICE_STATUS = 0x87

#
# 0x88 - 0x8E Unused
#

DEVICE_SIGNATURE = 0x8F
REGISTER_VALUES = 0x90
RAM_VALUES = 0x91
RAW_DATA = 0x92
HEARTBEAT = 0x93

#
# 0x94 - 0x9F Unused
#

def is_core_report_set(mdid):
        if mdid & 0xC0 == 192:
            return True
        elif mdid & 0x80 == 128:
            return True
        else:
            return False
