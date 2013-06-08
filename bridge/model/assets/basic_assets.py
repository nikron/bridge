from bridge.model.assets import Asset, Backing
from bridge.model.actions import action
from bridge.model.attributes import Attributes, BinaryAttribute, IntegerAttribute

class BlankAsset(Asset):
    """
    An asset placeholder for when you know something exists but you don't
    know what it is.
    """

    def __init__(self, real_id, service):
        super().__init__("", Attributes(), Backing(real_id, service, ""))
        self.failed_changes = []

    def change(self, attribute, state):
        self.failed_changes.append((attribute, state))

        return False

class OnOffAsset(Asset):
    """
    A device that is either simply on or off.
    """

    def __init__(self, name, real_id, service, product_name):
        attributes = Attributes(BinaryAttribute('main'))
        backing = Backing(real_id, service, product_name, on = ('turn_on', []), off = ('turn_off', []))
        super().__init__(name, attributes, backing)
        self.attributes.set_control('main', True, self.backing.get('on'))
        self.attributes.set_control('main', False, self.backing.get('off'))

    @action("Turn On")
    def turn_on(self):
        """
        Action to turn on the asset.
        """
        return self.backing.get('on')

    @action("Turn Off")
    def turn_off(self):
        """
        Action to turn off the asset.
        """
        return self.backing.get('off')

class DimmerAsset(Asset):
    """
    Class that represents a dimmable device.
    """

    def __init__(self, name, real_id, service, product_name):
        attributes = Attributes(IntegerAttribute('main', 0, 256))
        backing = Backing(real_id, service, product_name)
        super().__init__(name, attributes, backing)
        self._set_control_passthrough('main', 'set_light_level')

class VolumeAsset(Asset):
    """
    Class that represents a devicec with volume.
    """

    def __init__(self, name, real_id, service, product_name):
        attributes = Attributes(IntegerAttribute('main', 0, 101))
        backing = Backing(real_id, service, product_name)
        super().__init__(name, attributes, backing)
        self._set_control_passthrough('main', 'set_volume')
