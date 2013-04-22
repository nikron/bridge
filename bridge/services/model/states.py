"""
Triggers happen when an asset changes state.
"""
import uuid

from collections import defaultdict

class Trigger():
    def __init__(self, category, state, func):
        self.key = uuid.uuid1()
        self.category = category
        self.state = state
        self.func = func

    def __eq__(self, other):
        if self.key == other.key:
            return True
        else:
            return False

    def trigger(self):
        self.func()

class StateCategory():
    BINARY = 'binary'
    RANGE = 'range'

    def __init__(self, category, states):
        self.category = category
        self.current_state = 'unknown'

        if type(states) is range:
            self.type = self.RANGE

        elif len(states) == 2:
            self.type = self.BINARY

        else:
            raise TypeError('State is not binary or a range.')

        self.states = states
        self.triggers = defaultdict(lambda : [])

    def transition(self, state):
        if state in self.states:
            self.current_state = state

            for trigger in self.triggers[state]:
                trigger.trigger()

            return True

        else: return False

    def get_type(self):
        return self.type

    def add_trigger(self, trigger):
        self.triggers[trigger.state].append(trigger)

    def remove_trigger(self, trigger):
        del self.triggers[trigger.state]

    def serializable(self):
        ser = {}
        ser['current'] = self.current_state
        ser['type'] = self.type
        if self.type == self.RANGE:
            ser['possibilities'] = str(self.states)
        else:
            ser['possibilities'] = self.states

        return ser

    def __contains__(self, state):
        return state in self.states

    def __eq__(self, other):
        return self.category.__eq__(other.name)

    def __hash__(self):
        return self.category.__hash__()

    def __str__(self):
        return self.category


class States():
    """
    States is effectively a collection of categories that can have different states.  Currently can only trigger events when one category changes to a state.
    """
    def __init__(self, **states):

        self.categories = {}
        for state in states:
            self.categories[state] = StateCategory(state, states[state])

        self.triggers = []
        self.orient()

    def orient_trigger(self, trigger):
        self.categories[trigger.category].add_trigger(trigger)

    def orient(self):
        """Put triggers into the mesh."""
        for trigger in self.triggers:
            self.orient_trigger(trigger)

    def transition(self, category, state):
        """Attempt to transition to a state."""
        if category not in self.categories:
            return False
        elif state not in self.categories[category]:
            return False

        return self.categories[category].transition(state)

    def sudden_transition(self, category, state):
        """Change the current state without triggering any triggers."""
        if category not in self.categories:
            return False
        elif state not in self.categories[category]:
            return False

        self.categories[category].transition(state)

        return True

    def add_trigger(self, trigger):
        self.orient_trigger(trigger)

        self.triggers.append(trigger)

    def add_triggers(self, triggers):
        for trigger in triggers:
            self.add_trigger(trigger)

    def remove_trigger(self, trigger):
        self.triggers.remove(trigger)

        self.categories[trigger.category].remove_trigger(trigger)

    def serializable(self):
        ser = {}

        for category in self.categories:
            ser[str(category)] = self.categories[category].serializable()

        return ser
