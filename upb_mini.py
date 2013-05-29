#send a command over the serial port
#and print out resposne
import serial
from upb.pim import read
from upb import UPBMessage

ser = serial.Serial('/dev/ttyUSB0', '4800')
buf = b''

while True:
    msg = UPBMessage.create_from_packet(read(ser).packet)
    print(vars(msg))
