import uuid

class Trigger():
    def __init__(self, state1, state2, func):
        self.key = uuid.uuid1()
        self.state1 = state1
        self.state2 = state2
        self.func = func

    def __eq__(self, other):
        if self.key == other.key:
            return True
        else:
            return False

    def trigger(self):
        self.func()

class States():
    def __init__(self, current, states, triggers):
        self.states = {}

        self._internal_states(states)

        self.current = current

        self.triggers = triggers
        self.trigger_mesh = {}
        self.orient()

    #create the internal representative of a state
    def _internal_states(self, states):
        i = 1

        for state in states:
            self.states[state] = i
            i = i * 2

    def orient_trigger(self, trigger):
        edge = self.find_edge(trigger.state1, trigger.state2)

        if edge in self.trigger_mesh:
            self.trigger_mesh[edge].append(trigger)
        else:
            self.trigger_mesh[edge] = [trigger]

    def orient(self):
        for trigger in self.triggers:
            self.orient_trigger(trigger)

    def find_edge(self, state1, state2):
        #mildy sure taking a 2^n - 2^k where n and k are nonzero are unique
        #and n does not equal k
        edge = self.states[state1] - self.states[state2]
        return edge

    def transition(self, state):
        if state in self.states:
            return False

        edge = self.find_edge(self.current, state)
        self.current = state

        for trigger in self.trigger_mesh[edge]:
            trigger.trigger() #suck it

        return True

    #change state without triggering anything
    def sudden(self, state):
        self.current = state

    def add_trigger(self, trigger):
        self.orient_trigger(self, trigger)

        self.trigers.append(trigger)

    def remove_trigger(self, trigger):
        edge = self.find_edge(trigger.state1, trigger.state2)

        for trigger in self.trigger_mesh[edge]:
            if trigger.key == trigger:
                self.trigger_mesh[edge].remove(trigger)

        self.triggers.remove(trigger)

