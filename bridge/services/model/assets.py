"""
An asset is the internal representation of a device.
"""
from bridge.services.model.states import States, BinaryStateCategory, RangeStateCategory
from bridge.services.model.actions import Actions, action, get_actions
from bridge.services import BridgeMessage
import logging
import uuid


class Backing():
    """
    Backing attributes of an Asset.
    """

    def __init__(self, real_id, service, product_name, **message_args):
        self.real_id = real_id
        self.service = service
        self.product_name = product_name
        self.bridge_messages = {}

        self.add_messages(**message_args)

    def add_messages(self, **message_args):
        """
        Create a list of messages out of keyword arguments.
        """
        for name in message_args:
            method, args = message_args[name]
            msg = BridgeMessage.create_async(self.service, method, self.real_id, *args)
            self.bridge_messages[name] = msg

class Asset(metaclass = Actions):
    """
    Represent a physical device, such as a Keypadlinc.
    """

    def __init__(self, name, states, backing):
        self.states = states
        self.name = name
        self.backing = backing
        self.backing.add_messages(get_status = ('asset_info', []))

        self.uuid = uuid.uuid1()
        self.failed_transitions = []

    def get_control_message(self, category, state):
        """
        Get the control message for a category and state.
        """
        return self.states.get_control(category, state)

    def get_product_name(self):
        """
        The product name of the asset ie ApplianceLinc V2
        """
        return self.backing.product_name

    def get_real_id(self):
        """
        Real id of asset, (usually a str, definately a str for insteon (instead of bytes))
        """
        return self.backing.real_id

    def get_service(self):
        """
        Get the service the asset belongs to.
        """
        return self.backing.service

    def add_trigger(self, trigger):
        """
        Add trigger to on state change.
        """
        self.states.add_trigger(trigger)

    def serializable(self):
        """
        Return a form of the class that is easy to serialize (with JSON etc)
        """
        ser = {}
        ser['name'] = self.name
        ser['asset type'] = type(self).__name__
        ser['uuid'] = self.uuid
        ser['real id'] = self.get_real_id()
        ser['actions'] = get_actions(self)
        ser['state'] =  self.states.serializable()

        return ser

    def transition(self, category, state):
        """
        Change the asset state to state.
        """
        logging.debug("Going to state ({0},{1})".format(category, state))
        return self.states.transition(category, state)

    @action("Get Status")
    def get_status(self):
        """
        Uniform action of all assets, tries to get full status from IO.
        """
        return self.backing.bridge_messages['get_status']

class BlankAsset(Asset):
    """
    An asset placeholder for when you know something exists but you don't
    know what it is.
    """

    def __init__(self, real_id, service):
        super().__init__("", States(), Backing(real_id, service, ""))

    def transition(self, category, state):
        self.failed_transitions.append((category, state))

        return False

class OnOffAsset(Asset):
    """
    A device that is either simply on or off.
    """

    states = States(BinaryStateCategory('main'))

    def __init__(self, name, real_id, service, product_name):
        backing = Backing(real_id, service, product_name, on = ('turn_on', []), off = ('turn_off', []))
        super().__init__(name, self.states, backing)
        self.states.set_control('main', True, self.backing.bridge_messages['on'])
        self.states.set_control('main', False, self.backing.bridge_messages['off'])

    @action("Turn On")
    def turn_on(self):
        """
        Action to turn on the asset.
        """
        return self.backing.bridge_messages['on']

    @action("Turn Off")
    def turn_off(self):
        """
        Action to turn off the asset.
        """
        return self.backing.bridge_messages['off']

class DimmerAsset(Asset):
    """
    Class that represents a dimmable device.
    """

    states = States(RangeStateCategory('main', 0, 256))

    def __init__(self, name, real_id, service, product_name):
        backing = Backing(real_id, service, product_name)
        super().__init__(name, self.states, backing)
        def dim_level_to_message(num):
            return BridgeMessage.create_async(self.get_service(), 'go_to_level', self.get_real_id(), num)

        self.states.set_default_control('main', dim_level_to_message)

class VolumeAsset(Asset):
    """
    Class that represents a dimmable device.
    """

    states = States(RangeStateCategory('main', 0, 101))

    def __init__(self, name, real_id, service, product_name):
        backing = Backing(real_id, service, product_name)
        super().__init__(name, self.states, backing)
        def volume_to_message(num):
            return BridgeMessage.create_async(self.get_service(), 'set_volume', self.get_real_id(), num)

        self.states.set_default_control('main', volume_to_message)
