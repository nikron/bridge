"""
An asset is the internal representation of a device.
"""
from bridge.services.model.states import States, BinaryStateCategory
from bridge.services.model.actions import Actions, action, get_actions
from bridge.service import BridgeMessage
import logging
import uuid


class Backing():
    """Backing attributes of an Asset."""
    def __init__(self, real_id, service, product_name, io_args):
        self.real_id = real_id
        self.service = service
        self.product_name = product_name
        self.io_args = io_args
        self.bridge_messages = []

        self._create_messages()

    def _create_messages(self):
        for method, args in self.io_args:
            self.bridge_messages.append(BridgeMessage.create_async(self.service, method, self.real_id, *args))

class Asset(metaclass = Actions):
    """
    Represent a physical device, such as a Keypadlinc.
    """

    def __init__(self, name, states, backing):
        self.states = states
        self.name = name
        self.backing = backing

        self.uuid = uuid.uuid1()
        self.failed_transitions = []

    def transition(self, category, state):
        """Change the asset state to state."""
        logging.debug("Going to state ({0},{1})".format(category, state))
        return self.states.transition(category, state)

    def add_trigger(self, trigger):
        """Add trigger to on state change."""
        self.states.add_trigger(trigger)

    def get_name(self):
        return self.name

    def get_real_id(self):
        """Real id of asset, (usually a str, definately a str for insteon (instead of bytes))"""
        return self.backing.real_id

    def get_service(self):
        return self.backing.service

    def get_product_name(self):
        """The product name of the asset ie ApplianceLinc V2"""
        return self.backing.product_name

    def get_control_message(self, category, state):
        return self.states.get_control(category, state)

    def set_name(self, name):
        self.name = name

    def serializable(self):
        """Return a form of the class that is easy to serialize (with JSON etc)"""
        ser = {}
        ser['name'] = self.name
        ser['asset type'] = type(self).__name__
        ser['uuid'] = self.uuid
        ser['real id'] = self.get_real_id()
        ser['actions'] = get_actions(self)
        ser['state'] =  self.states.serializable()

        return ser


class BlankAsset(Asset):
    """
    An asset placeholder for when you know something exists but you don't
    know what it is.
    """

    def __init__(self, real_id, service):
        super().__init__("", States(), Backing(real_id, service, "", []))

    def transition(self, category, state):
        self.failed_transitions.append((category, state))

        return False

class OnOffAsset(Asset):
    """
    A device that is either simply on or off.
    """

    on_off_states = States(BinaryStateCategory('main'))

    def __init__(self, name, real_id, service, product_name):
        backing = Backing(real_id, service, product_name, [('turn_on', []), ('turn_off', [])])
        super().__init__(name, self.on_off_states, backing)
        self.states.set_control('main', True, self.backing.bridge_messages[0])
        self.states.set_control('main', False, self.backing.bridge_messages[1])

    @action("Turn On")
    def turn_on(self):
        """Action to turn on the asset."""
        self.states.transition('main', 'unknown')

        return self.backing.bridge_messages[0]

    @action("Turn Off")
    def turn_off(self):
        """Action to turn off the asset."""
        self.states.transition('main', 'unknown')

        return self.backing.bridge_messages[1]
