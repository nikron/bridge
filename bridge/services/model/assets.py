#assets are classes for individual devices
import uuid

class Asset():
    def __init__(self, real_id, current, states, triggers):
        self.states = States(current, states, triggers)
        self.uuid = uuid.uuid1()
        self.real_id = real_id

    def transition(state):
        self.states.transition(state)

class OnOffAsset(Asset):
    state_names = ['unknown', 'on', 'off', 'pending on', 'pending off']
    def __init__(self, real_id, events, current='unknown', None):
        super().__init__(real_id, current, self.state_names, events)

    def turn_off(self):
        self.transition('pending off')

    def turn_on(self):
        self.transition('pending on')
