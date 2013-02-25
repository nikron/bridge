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
        i = 1

        for state in states:
            self.states[state] = i
            i = i * 2

        self.current = current

        self.triggers = triggers
        self.trigger_mesh = {}
        self.orient()

    def orient_trigger(self, trigger):
        edge = self.find_edge(trigger.state1, trigger.state2)

        if edge in self.trigger_mesh:
            self.trigger_mesh[edge].append(trigger)
        else:
            self.trigger_mesh[edge] = [trigger]

    def orient(self):
        for trigger in self.triggers:
            self.orient_trigger(trigger)

    def transition(self, state):
        #mildy sure taking a 2^n - 2^k where n and k are nonzero are unique
        edge = self.find_edge(self.current,state)
        self.current = state

        for trigger in self.trigger_mesh[edge]:
            trigger.trigger() #suck it

    def find_edge(self, state1, state2):
        edge = self.states[state1] - self.states[state2]
        return edge

    def add_trigger(self, trigger):
        self.orient_trigger(self, trigger)

        self.trigers.append(trigger)

    def remove_trigger(self, trigger):
        edge = self.find_edge(trigger.state1, trigger.state2)

        for trigger in self.trigger_mesh[edge]:
            if trigger.key == trigger:
                self.trigger_mesh[edge].remove(trigger)

        self.triggers.remove(trigger)

