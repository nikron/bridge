"""
An asset is the internal representation of a device.
"""
from bridge.services.model.states import States
from bridge.services.model.actions import Actions, action, get_actions
import logging
import uuid


class Backing():
    """Backing attributes of an Asset."""
    def __init__(self, real_id, product_name, actuple):
        self.real_id = real_id
        self.product_name = product_name
        self.actuple = actuple

class Asset(metaclass = Actions):
    """
    Represent a physical device, such as a Keypadlinc.
    """

    def __init__(self, name, states, backing):
        self.states = states
        self.name = name
        self.backing = backing

        self.uuid = uuid.uuid1()
        self.failed_transistions = []

    def transition(self, category, state):
        """Change the asset state to state."""
        logging.debug("Going to state ({0},{1})".format(category, state))
        return self.states.transition(category, state)

    def add_trigger(self, trigger):
        """Add trigger to on state change."""
        self.states.add_trigger(trigger)

    def current_states(self):
        """Get the current categories and states of this asset."""
        return self.states.current_states()

    def get_real_id(self):
        """Real id of asset, (usually a str, definately a str for insteon (instead of bytes))"""
        return self.backing.real_id

    def get_product_name(self):
        """The product name of the asset ie ApplianceLinc V2"""
        return self.backing.product_name

    def serializable(self):
        """Return a form of the class that is easy to serialize (with JSON etc)"""
        ser = {}
        ser['name'] = self.name
        ser['asset type'] = type(self).__name__
        ser['uuid'] = self.uuid
        ser['real id'] = self.get_real_id()
        ser['actions'] = get_actions(self)
        ser['state'] =  self.states.current_states()

        return ser


class BlankAsset(Asset):
    """
    An asset placeholder for when you know something exists but you don't
    know what it is.
    """

    def __init__(self, real_id):
        super().__init__("", States({}, []), Backing(real_id, "", []))

    def transition(self, category, state):
        self.failed_transistions.append((category, state))

        return False

class OnOffAsset(Asset):
    """
    A device that is either simply on or off.
    """

    on_off_states = States({'main' : {'unknown', 'pending on', 'pending off', 'off', 'on'}}, [])

    def __init__(self, name, backing):
        super().__init__(name, self.on_off_states, backing)
        self.on_off_states.sudden('main', 'unknown')

    @action("Turn On")
    def turn_on(self):
        """Action to turn on the asset."""
        self.states.transition('main', 'unknown')

        return self.backing.actuple[0]

    @action("Turn Off")
    def turn_off(self):
        """Action to turn off the asset."""
        self.states.transition('main', 'unknown')

        return self.backing.actuple[1]
