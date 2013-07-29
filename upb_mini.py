#send a command over the serial port
#and print out resposne
import serial
from upb.pim import write_message, read
import upb

ser = serial.Serial('/dev/ttyUSB0', '4800')
msg = upb.UPBGoToLevel(100)
msg.destination_id = 45
print(read(ser).packet)
