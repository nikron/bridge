#send a command over the serial port
#and print out resposne
import serial
from insteon_protocol.command import commands

#CHANGE THIS FOR NON LINUX SYSTEMS
#example /dev/cu.usbserial-asdf
ser = serial.Serial('/dev/ttyUSB0', '19200')
buff = b''

cmd = commands.TurnOnFast(b'\x01\x3A\x26')
ser.write(cmd.encode())

while True:
	if (ser.inWaiting() > 0):
		buff = buff + ser.read(ser.inWaiting())
		print(buff)

