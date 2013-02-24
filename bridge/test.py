#from ..device import Device, LampLinc
#from ..command import TurnOn

from services.insteon.command_encode.device import Device, LampLinc
from services.insteon.command_encode.device import TurnOn

device = LampLinc()
response = device.encodeCommand(TurnOn, "010203")
print(response)

print (device.decodeCommand(response + "06").get("ack"))
print (device.decodeCommand(response + "15").get("ack"))

