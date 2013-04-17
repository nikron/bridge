"""
Triggrs happen when an asset changes state.
"""
import uuid

from collections import namedtuple

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

class Category():
    def __init__(self, current_state, states):
        self.current_state = current_state
        self.states = states

class States():
    """
    States is effectively a collection of categories that can have different states.
    Currently can only trigger events when one category changes to a state.
    """
    def __init__(self, categories, triggers):

        self.categories = {}
        for category in categories:
            self.categories[category] = Category('', {})

            for state in categories[category]:
                self.categories[category].states[state] = []

        self.triggers = triggers
        self.orient()

    def orient_trigger(self, trigger):
        self.categories[trigger.category].states[trigger.state].append(trigger)

    def orient(self):
        """Put triggers into the mesh."""
        for trigger in self.triggers:
            self.orient_trigger(trigger)

    def transition(self, category, state):
        """Attempt to transition to a state."""
        if category not in self.categories:
            return False
        elif state not in self.categories[category].states:
            return False

        self.categories[category].current_state = state

        for trigger in self.find_triggers(category, state):
            trigger.trigger() #suck it

        return True

    def sudden_transistion(self, category, state):
        """Change the current state without triggering any triggers."""
        if category not in self.categories:
            return False
        elif state not in self.categories[category].states:
            return False

        self.categories[category].current_state = state

        return True

    def find_triggers(self, category, state):
        return self.categories[category].states[state]

    def add_trigger(self, trigger):
        self.orient_trigger(trigger)

        self.triggers.append(trigger)

    def add_triggers(self, triggers):
        for trigger in triggers:
            self.add_trigger(trigger)

    def remove_trigger(self, trigger):
        self.triggers.remove(trigger)

        self.categories[trigger.category].states[trigger.state].remove(trigger)

    def current_states(self):
        current = {}

        for category in self.categories:
            current[category] = self.categories[category].current_state

        return current
