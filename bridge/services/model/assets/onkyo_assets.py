from bridge.services.model.assets import Asset, Backing
from bridge.services.model.states import States, IntegerRangeStateCategory, BinaryStateCategory

class OnkyoTXNR609(Asset):
    states = States(BinaryStateCategory('main'),
            IntegerRangeStateCategory('volume', 0, 101),
            BinaryStateCategory('mute'))

    def __init__(self, name, real_id, service, product_name):
        backing = Backing(real_id, service, product_name)
        super().__init__(name, self.states, backing)
        self._set_control_passthrough('main', 'set_power')
        self._set_control_passthrough('volume', 'set_volume')
        self._set_control_passthrough('mute', 'set_mute')
