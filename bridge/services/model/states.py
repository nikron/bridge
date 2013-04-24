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
    def __init__(self, category, states, _type):
        self.category = category
        self.current_state = None
        self.states = states
        self.unknown = True
        self.controllable = False
        self.default_control = None
        self.type = _type

        self.triggers = defaultdict(lambda : [])
        self.controls = {}

    def add_trigger(self, trigger):
        self.triggers[trigger.state].append(trigger)

    def get_category(self):
        return self.category

    def get_type(self):
        return self.type

    def get_control(self, state):
        #maybe raise an error if not controllable, probably shouldn't
        if state in self.controls:
            return self.controls[state]
        else:
            return self.default_control(state)

    def remove_trigger(self, trigger):
        del self.triggers[trigger.state]

    def serializable(self):
        ser = {}
        ser['current'] = self.current_state
        ser['type'] = self.type
        ser['controllable'] = self.controllable
        ser['unknown'] = self.unknown
        ser['possible states'] = self.states

        return ser

    def set_default_control(self, func):
        self.default_control = func
        self._check_controllable()

    def set_control(self, state, control):
        self.controls[state] = control
        self.controllable = True
        self._check_controllable()

    def set_unknown(self, unknown):
        if unknown:
            self.current = None

        self.unknown = unknown

    def transition(self, state):
        if state in self.states:
            self.current_state = state

            for trigger in self.triggers[state]:
                trigger.trigger()

            self.set_unknown(False)
            return True

        else: return False

    def _check_controllable(self):
        if self.default_control:
            self.controllable = True
        else:
            self.controllable = True
            for state in self.states:
                if state not in self.controls:
                    self.controllable = False
                    return

    def __contains__(self, state):
        return state in self.states

    def __eq__(self, other):
        return self.category.__eq__(other.name)

    def __hash__(self):
        return self.category.__hash__()

    def __str__(self):
        return self.category

class BinaryStateCategory(StateCategory):
    BINARY_TYPE = 'binary'
    def __init__(self, category):
        super().__init__(category, [True, False], self.BINARY_TYPE)

class States():
    """
    States is effectively a collection of categories that can have different states.  Currently can only trigger events when one category changes to a state.
    """
    def __init__(self, *states):

        self.categories = {}
        for state in states:
            self.categories[state.get_category()] = state

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

    def get_control(self, category, state):
        return self.categories[category].get_control(state)

    def remove_trigger(self, trigger):
        self.triggers.remove(trigger)

        self.categories[trigger.category].remove_trigger(trigger)

    def set_default_control(self, category, state, control):
        self.categories[category].set_default_control(control)

    def set_control(self, category, state, control):
        self.categories[category].set_control(state, control)

    def serializable(self):
        ser = {}

        for category in self.categories:
            ser[str(category)] = self.categories[category].serializable()

        return ser
