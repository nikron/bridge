#send a command over the serial port
#and print out resposne
import serial
from insteon_protocol.command import im_commands
from insteon_protocol.insteon_im_protocol import read_command, decode

#CHANGE THIS FOR NON LINUX SYSTEMS
#example /dev/cu.usbserial-asdf
ser = serial.Serial('/dev/ttyUSB0', '19200')
buff = b''

#cmd = commands.ProductDataRequest(b'\x01\x3A\x26')
#cmd = im_commands.TurnOff(b'\x00\xF1\xD1')
#cmd = im_commands.GetINSTEONVersion(b'\x00\xF1\xD1')
cmd = im_commands.TurnOnLevel(b'\x1A\xD9\x8E', b'\xfe')
#cmd = im_commands.LightStatusRequest(b'\x1a\xd9\x8e')
#cmd = commands.TurnOff(b'\x00\x00\x01')
print("Writing {0} to IM.".format(str(cmd.encode())))
print(b'\x02b\xa1\xd9\x8e\x0f\x11\xfe')
print(cmd.encode())
ser.write(b'\x02b\xa1\xd9\x8e\x0f\x11\xfe')

while True:
    buf = read_command(ser)
    print("Read {0} from IM.".format(str(buf)))
    obj = decode(buf)
    print(obj)
