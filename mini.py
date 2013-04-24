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
cmd = im_commands.TurnOff(b'\x00\xF1\xD1')
#cmd = im_commands.GetINSTEONVersion(b'\x00\xF1\xD1')
#cmd = commands.TurnOffFast(b'\x01\x3A\x26')
#cmd = commands.ProductDataRequest(b'\x00\x00\x01')
#cmd = commands.TurnOff(b'\x00\x00\x01')
print("Writing {0} to IM.".format(str(cmd.encode())))
ser.write(cmd.encode())

while True:
    buf = read_command(ser)
    print("Read {0} from IM.".format(str(buf)))
    obj = decode(buf)
    print(obj)
