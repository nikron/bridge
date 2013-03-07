#assets are classes for individual devices
from bridge.services.model.states import States
import logging
import uuid

class Asset():
    def __init__(self, real_id, current, states, allowable, triggers):
        self.states = States(current, states, triggers)
        self.uuid = uuid.uuid1()
        self.real_id = real_id
        self.outside_states = allowable
        self.failed_transistions = []

    def transition(self, state):
        self.states.transition(state)

    def outside_transition(self, state):
        if state in self.outside_states:
            self.transition(state)
        else:
            logging.error("State " + repr(state) + " not in allowable outside states.")

    def update(self, up):
        pass

"""
An asset placeholder for when you know something exists but you don't
know what it is.
"""
class BlankAsset(Asset):
    def __init__(self, real_id):
        super().__init__(self, real_id, None, None, None, None) 

    def transition(self, state):
        self.failed_transistions.append(state)

        return False

    def outside_transition(self, state):
        self.failed_transistions.append(state)

        return False

class OnOffAsset(Asset):
    state_names = ['unknown', 'on', 'off', 'pending on', 'pending off']
    allowable = ['pending on', 'pending off']
    def __init__(self, real_id, triggers, current='unknown'):
        super().__init__(real_id, current, self.state_names, self.allowable, triggers)

    def turn_off(self):
        self.transition('pending off')

    def turn_on(self):
        self.transition('pending on')
