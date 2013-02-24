#from ..device import Device, LampLinc
#from ..command import TurnOn

from services.insteon.command_encode.device import Device, LampLinc
from services.insteon.command_encode.device import TurnOn

response = Device.encodeCommandForDevice(Device, TurnOn, "010203", LampLinc)
print(response)

print (Device.decodeCommandFromDevice(Device, response + "06").get("ack"))
print (Device.decodeCommandFromDevice(Device, response + "15").get("ack"))

