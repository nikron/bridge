"""
Metaclass to designate a methods of a class `actions` using
a decorator.
"""

from inspect import getargspec
import logging

def action(name):
    """Decorator that accepts name as pretty name for a method to be an action of
    its object."""
    def wrapper(func):
        func.__isaction__ = True
        func.__pretty_name__ = name
        return func

    return wrapper

def _get_action_func(obj, act):
    """Internal function to get action of object or raise error."""
    try:
        return getattr(obj, act)

    except AttributeError:
        logging.debug("Asset {0} does not have action {1}.".format(getattr(obj, '__name__'), action))
        raise ActionError("Asset does not have action `{0}`.".format(action))

def get_actions(obj):
    """Get all actions of obj."""
    return list(obj.__actions__)

def perform_action(obj, act, *args, **kwargs):
    """Perform an action on obj."""
    try:
        _get_action_func(obj, act)(*args, **kwargs)
    except TypeError:
        raise ActionError("Incorrect arguments.")


#maybe cache this information
def get_action_information(obj, action):
    action = _get_action_func(obj, action)
    info = {}
    info['name'] = action.__pretty_name__
    info['arguments'] =  getargspec(action).args[1:] #to not include self.

    return info


class ActionError(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


#you ask why I'd do it this way, I say for fun
class Actions(type):
    def __new__(mcls, names, bases, namespace):
        cls = super().__new__(mcls, names, bases, namespace)

        actions = {name for name, value in namespace.items() if getattr(value, '__isaction__', False)}

        for base in bases:
            actions = actions.union(getattr(base, '__actions__', set()))

        cls.__actions__ = frozenset(actions)

        return cls