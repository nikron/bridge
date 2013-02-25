from abc import ABCMeta, abstractmethod
import uuid

class States():
    def __init__(self, current, states):
        self.states = {}
        i = 1

        for state in states:
            self.states[state] = i
            i = i * 2

        self.current = current # assume the first state is the first current
        #state

    def transition(self, state):
        #mildy sure taking a 2^n - 2^k where n and k are nonzero are unique
        edge = self.find_edge(self.current,state)
        self.current = state

        return edge

    def find_edge(self, state1, state2):
        edge = self.states[state1] - self.states[state2]
        return edge

class Asset(metaclass=ABCMeta):
    def __init__(self, real_id, current, states, events):
        self.states = States(current, states)

        events.orient(states)
        self.events =  events

        self.uuid = uuid.uuid1()
        self.real_id = real_id


    def state_transition(state):
        edge = self.states.transition(state)
        self.events.trigger(edge)


class OnOffAsset(Asset):
    state_names = ['unknown', 'on', 'off', 'pending on', 'pending off']
    def __init__(self, real_id, events, current='unknown'):
        super().__init__(real_id, current, self.state_names, events)

    def turn_off(self):
        self.state_transition('off')

    def turn_on(self):
        self.state_transition('off')
