"""
An asset is the internal representation of a device.
"""
from bridge.services.model.states import States
from bridge.services.model.actions import Actions, action
import logging
import uuid


class Backing():
    def __init__(self, real_id, product_name):
        self.real_id = real_id
        self.product_name = product_name

class Asset(metaclass=Actions):
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
        return self.states.transition(category, state)

    def current_states(self):
        return self.states.current_states()

    def get_real_id(self):
        return self.backing.real_id

    def get_product_name(self):
        return self.backing.product_name

class BlankAsset(Asset):
    """
    An asset placeholder for when you know something exists but you don't
    know what it is.
    """

    def __init__(self, real_id):
        super().__init__("", None, Backing(real_id, "")) 

    def transition(self, category, state):
        self.failed_transistions.append((category, state))

        return False

class OnOffBacking(Backing):
    def __init__(self, real_id, product_name, on_func, off_func):
        super().__init__(real_id, product_name)
        self.on_func = on_func
        self.off_func = off_func

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
        self.backing.on_func()
        self.states.transition('main', 'unknown')

        return True

    @action("Turn Off")
    def turn_off(self):
        self.backing.off_func()
        self.states.transition('main', 'unknown')

        return True
