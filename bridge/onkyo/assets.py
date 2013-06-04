from bridge.model.assets import Asset, Backing
from bridge.model.attributes import Attributes, IntegerRangeAttribute, BinaryAttribute

class OnkyoTXNR609(Asset):

    def __init__(self, name, real_id, service, product_name):
        attributes = attributes(BinaryAttribute('main'),
                IntegerRangeAttribute('volume', 0, 101),
                BinaryAttribute('mute'))
        backing = Backing(real_id, service, product_name)
        super().__init__(name, attributes, backing)
        self._set_control_passthrough('main', 'set_power')
        self._set_control_passthrough('volume', 'set_volume')
        self._set_control_passthrough('mute', 'set_mute')
