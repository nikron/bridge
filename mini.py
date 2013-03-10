#send a command over the serial port
#and print out resposne
import serial
from insteon_protocol.command import commands

#CHANGE THIS FOR NON LINUX SYSTEMS
#example /dev/cu.usbserial-asdf
ser = serial.Serial('/dev/ttyUSB1', '19200')
buff = b''

#cmd = commands.ProductDataRequest(b'\x01\x3A\x26')
cmd = commands.TurnOff(b'\x1A\xD9\x8E')
#cmd = commands.TurnOffFast(b'\x01\x3A\x26')
#cmd = commands.ProductDataRequest(b'\x00\x00\x01')
#cmd = commands.TurnOff(b'\x00\x00\x01')
ser.write(cmd.encode())

while True:
	if (ser.inWaiting() > 0):
		buff = buff + ser.read(ser.inWaiting())
		print(buff)

