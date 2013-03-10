"""
An asset is the internal representation of a device.
"""
from bridge.services.model.states import States
import logging
import uuid

class Asset():
    """
    Represent a physical device, such as a Keypadlinc.
    """
    def __init__(self, real_id, current, states, allowable, triggers):
        self.states = States(current, states, triggers)
        self.uuid = uuid.uuid1()
        self.real_id = real_id
        self.outside_states = allowable
        self.failed_transistions = []

    def tranistion(self, state):
        """Change the asset state to state."""
        self.states.transition(state)

    def outside_transition(self, state):
        """Change the asset state to one allowed by non bridge things."""
        if state in self.outside_states:
            self.transition(state)
        else:
            logging.error("State {0} not in allowable outside states.".format(
                repr(state)))

class BlankAsset(Asset):
    """
    An asset placeholder for when you know something exists but you don't
    know what it is.
    """

    def __init__(self, real_id):
        super().__init__(real_id, None, [], [], []) 

    def tranistion(self, state):
        self.failed_transistions.append(state)

        return False

    def outside_transition(self, state):
        self.failed_transistions.append(state)

        return False

class OnOffAsset(Asset):
    """
    A device that is either simply on or off.
    """

    state_names = ['unknown', 'on', 'off', 'pending on', 'pending off']
    allowable = ['pending on', 'pending off']

    def __init__(self, real_id, triggers, current='unknown'):
        super().__init__(real_id, current, self.state_names, self.allowable, triggers)
