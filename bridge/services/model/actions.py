"""
Metaclass to designate a methods of a class `actions` using
a decorator.
"""

from inspect import getargspec

def action(name):
    def wrapper(func):
        func.__isaction__ = True
        func.__pretty_name__ = name
        return func

    return wrapper

def _get_action_func(obj, action):
    return getattr(obj, action)

def get_actions(obj):
    return list(obj.__actions__)

def perform_action(obj, action, *args, **kwargs):
    action = _get_action_func(obj, action)(*args, **kwargs)


#maybe cache this information
def get_action_information(obj, action):
    action = _get_action_func(obj, action)
    info = {}
    info['name'] = action.__pretty_name__
    info['arguements'] = argspec(action).args


#you ask why I'd do it this way, I say for fun
class Actions(type):
    def __new__(mcls, names, bases, namespace):
        cls = super().__new__(mcls, names, bases, namespace)

        actions = {name for name, value in namespace.items() if getattr(value, '__isaction__', False)}

        for base in bases:
            actions = actions.union(getattr(base, '__actions__', set()))

        cls.__actions__ = frozenset(actions)

        return cls
