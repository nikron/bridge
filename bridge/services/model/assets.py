"""
An asset is the internal representation of a device.
"""
from bridge.services.model.states import States
import logging
import uuid

def action(func):
    func.__isaction__ = True
    return func

#you ask why I'd do it this way, I say for fun
class Actions(type):
    def __new__(mcls, names, bases, namespace):
        cls = super().__new__(mcls, names, bases, namespace)
        actions = {name for name, value in namespace.items() if getattr(value, '__isaction__', False)}

        for base in bases:
            base_actions = getattr(base, '__actions__', set())
            actions = actions.union(base_actions)

        cls.__actions__ = frozenset(actions)

        return cls

class Backing():
    def __init__(self, real_id):
        self.real_id = real_id

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

    def get_real_id(self):
        return self.backing.real_id

    def get_actions(self):
        return self.__actions__

    def perform_action(self, action, *args):
        act = getattr(self, action, None)
        if act is not None:
            act(*args)
            return True

        return False

class BlankAsset(Asset):
    """
    An asset placeholder for when you know something exists but you don't
    know what it is.
    """

    def __init__(self, name, backing):
        super().__init__(name, None, backing) 

    def transition(self, category, state):
        self.failed_transistions.append((category, state))

        return False

class OnOffBacking(Backing):
    def __init__(self, real_id, on_func, off_func):
        super().__init__(real_id)
        self.on_func = on_func
        self.off_func = off_func

class OnOffAsset(Asset):
    """
    A device that is either simply on or off.
    """

    on_off_states = States({'main' : {'unknown', 'pending on', 'pending off', 'off', 'on'}}, [])

    def __init__(self, name, backing):
        super().__init__(name, self.on_off_states, backing)

    @action
    def turn_on(self):
        self.backing.on_func()
        self.states.transition('main', 'unknown')

        return True

    @action
    def turn_off(self):
        self.backing.off_func()
        self.states.transition('main', 'unknown')

        return True
