#send a command over the serial port
#and print out resposne
import serial
from upb.pim import write_message
import upb

ser = serial.Serial('/dev/ttyUSB0', '4800')
msg = upb.UPBGoToLevel(0)
msg.destination_id = 5

write_message(ser, msg)
