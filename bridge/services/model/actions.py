"""
Actions are things the user can do that don't have a defined result other
than what their name indicates.  Also known as buttons; things like volume up,
dimmer down, open garage that don't make sense as a state should be an action.
"""

from inspect import getargspec
import logging

class Actions(type):
    """
    Metaclass that makes designated functions of a class into special `action` functions,
    essentially functions with more metadata.
    """
    def __new__(mcls, names, bases, namespace):
        cls = super().__new__(mcls, names, bases, namespace)

        actions = {name for name, value in namespace.items() if getattr(value, '__isaction__', False)}

        for base in bases:
            actions = actions.union(getattr(base, '__actions__', set()))

        cls.__actions__ = frozenset(actions)

        return cls

class ActionError(Exception):
    """Simple error for actions."""
    def __init__(self, message):
        super().__init__()
        self.message = message

def action(name):
    """
    Decorator that makes a function an action.  The name given is the
    one presented to clients, who will probably present it to users.

    :param name: Pretty name of the action.
    :type func: str
    """
    def wrapper(func):
        """
        The new function, set some attributes of an action function.

        :param func: The function to become an action.
        :type func: func
        """
        func.__isaction__ = True
        func.__pretty_name__ = name
        return func

    return wrapper

def get_actions(obj):
    """
    Get all actions of obj.
    """
    return list(obj.__actions__)

def get_action_information(obj, act):
    """
    Get metadata of an action.
    """
    action_func = _get_action_func(obj, act)
    info = {}
    info['name'] = action_func.__pretty_name__
    info['arguments'] =  getargspec(action_func).args[1:] #to not include self.

    return info

def perform_action(obj, act, *args, **kwargs):
    """Perform an action on obj."""
    try:
        return _get_action_func(obj, act)(*args, **kwargs)
    except TypeError:
        raise ActionError("Incorrect arguments.")

def _get_action_func(obj, act):
    """
    Internal function to get action of object or raise error.

    :param obj:
    :type obj: object

    :param act:
    :type act: str
    """
    try:
        return getattr(obj, act)

    except AttributeError:
        logging.debug("Asset {0} does not have action {1}.".format(getattr(obj, '__name__'), action))
        raise ActionError("Asset does not have action `{0}`.".format(action))
