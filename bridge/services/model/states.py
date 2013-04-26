"""
Meant to hold the status/state/attributes of a device.  Anything that will change
on a device and should be controlled is considered a state.  Examples: lighting, volume,
and status of LED buttons.
"""
import uuid

from collections import defaultdict

class States():
    """
    A collection of independant :class:`StateCategory`s.  A state is meant to be changed by transition
    a category (of states) to another state.  Another important function of a state is the notion of whether
    it is "controllable", it is considered controllable if all of its possible states have a control object
    associated with it.

    States also currently will allow firing off a function whena paticular transition happens;
    this feature may or may not be removed/changed in the near future.

    :param *states: List of :class:`StateCategory`(s)
    :type *states: [:class:`StateCategory`]
    """
    def __init__(self, *states):
        self.categories = {}
        for state in states:
            self.categories[state.get_category()] = state

        self.triggers = []

    def add_trigger(self, trigger):
        """
        Add a trigger.

        :param trigger: :class:`Trigger` to add.
        :type trigger: :class:`Trigger`
        """
        self.orient_trigger(trigger)
        self.triggers.append(trigger)

    def get_control(self, category, state):
        """
        Get a control object from a category for a state.  This object
        is intended to be one that allows for control of the device, such as a
        :class:`BridgeMessage`.

        :param category: The category to get the control object.
        :type category: str

        :param state: The state that the object controls.
        :type state: str

        :return: The control object associated with changing to a state.
        :rtype: object
        """
        return self.categories[category].get_control(state)

    def orient_trigger(self, trigger):
        """
        Add a trigger to a :class:`StateCategory`.

        :param trigger: The trigger to add.
        :type trigger: :class:`Trigger`
        """
        self.categories[trigger.category].add_trigger(trigger)

    def remove_trigger(self, trigger):
        """
        Remove a trigger to a :class:`StateCategory`.

        :param trigger: The trigger to remove.
        :type trigger: :class:`Trigger`
        """
        self.triggers.remove(trigger)
        self.categories[trigger.category].remove_trigger(trigger)

    def serializable(self):
        """
        Return a representation of the :class:`States` in a form of only python
        primitives, one that is easy to serialize.

        :return: The serilizable dictionary representing this :class:`States`.
        :rtype: dict
        """
        ser = {}

        for category in self.categories:
            ser[str(category)] = self.categories[category].serializable()

        return ser

    def set_default_control(self, category, control):
        """
        Set a callable object on a category, the object will be called
        with the target state and the result will be returned when :func:`get_control`.

        :param category: The category to get the control object.
        :type category: str

        :param param: The control object
        :type object:
        """
        self.categories[category].set_default_control(control)

    def set_control(self, category, state, control):
        """
        Set an object to be returned on :func:`get_control`, if a :class:`StateCategory`'s
        all possible states have control objects, that :class:`StateCategory` will be considered
        controllable.

        :param category: The category to get set control object.
        :type category: str

        :param state: The state that the object controls.
        :type state: str

        :param param: The control object
        :type object:
        """
        self.categories[category].set_control(state, control)

    def sudden_transition(self, category, state):
        """
        Attempt to transition a category to a paticular state.
        Will not call any triggers

        :param category: The category to change.
        :type category: str

        :param state: The state to transition to.
        :type state: str

        :return: Whether the transition was successful.
        :rtype: bool
        """
        if category not in self.categories:
            return False

        return self.categories[category].transition(state)

    def transition(self, category, state):
        """
        Attempt to transition a category to a paticular state.
        If succesful will also call any attached triggers.

        :param category: The category to change.
        :type category: str

        :param state: The state to transition to.
        :type state: str

        :return: Whether the transition was successful.
        :rtype: bool
        """
        if category not in self.categories:
            return False

        return self.categories[category].transition(state)

class StateCategory():
    """
    A category of states, keeps track of various attributres of state, most
    of important of which are whether it is "controllable", and whether the current
    state is "known".

    :param category: The name of the category
    :type category: str

    :param states: A list like object that has all possible states of an object.
    :type states: object

    :param _type: The type of category it is, intended for clients to know what kind of control to display for this state
    :type _type: str
    """
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
        """
        Add a trigger to a state.

        :param trigger: :class:`Trigger` to add.
        :type trigger: :class:`Trigger`
        """
        self.triggers[trigger.state].append(trigger)

    def get_category(self):
        """
        :return: The category of states that this object represents.
        :rtype: str
        """
        return self.category

    def get_control(self, state):
        """
        Return an object that is used to change this catgory to a state. If
        there is an object directly associated with the paticular state,then
        try to use a default control function to create an object.

        :param state: State of the correspondoing control object
        :type state: str

        :return: The way to change to this state.
        :rtype: object
        """
        #maybe raise an error if not controllable, probably shouldn't
        if state in self.controls:
            return self.controls[state]
        else:
            return self.default_control(state)

    def get_type(self):
        """
        :return: The type of category this object represents.
        :rtype: str
        """
        return self.type

    def remove_trigger(self, trigger):
        """
        Remove a trigger.

        :param trigger: :class:`Trigger` to remove.
        :type trigger: :class:`Trigger`
        """
        del self.triggers[trigger.state]

    def serializable(self):
        """
        :return: Return a form of this category easy to serialize.
        :rtype: dict
        """
        ser = {}
        ser['current'] = self.current_state
        ser['type'] = self.type
        ser['controllable'] = self.controllable
        ser['unknown'] = self.unknown
        ser['possible states'] = self.states

        return ser

    def set_control(self, state, control):
        """
        Set the control object for a state, make it controllable if all possible states have controls.

        :param state: State to set control to
        :type state: str

        :param control: Control to change the state.
        :type control: object
        """
        self.controls[state] = control
        self.controllable = True
        self._check_controllable()

    def set_default_control(self, func):
        """
        Make the category controllable by having a default callable object
        when there is no specific object associated with a state.

        :param func: Callable object that be called with the intended state.
        :type func: object
        """
        self.default_control = func
        self._check_controllable()

    def set_unknown(self, unknown):
        """
        Set the current state knowledge, will remove the current state
        if it is uknown is False.

        :param unknown: If the current state is known or not.
        :type unknown: bool
        """
        if unknown:
            self.current_state = None

        self.unknown = unknown

    def sudden_transition(self, state):
        """
        Makes the current state known to be state.
        Does not fire off any triggers.

        :param state: State to transition to.
        :type state: str
        """
        if state in self.states:
            self.current_state = state

            self.set_unknown(False)
            return True

        else: return False

    def transition(self, state):
        """
        Makes the current state known to be state.

        :param state: State to transition to.
        :type state: str
        """
        if state in self.states:
            self.current_state = state

            for trigger in self.triggers[state]:
                trigger.trigger()

            self.set_unknown(False)
            return True

        else: return False

    def _check_controllable(self):
        """
        Check if all the possible states have a control object
        associated with them, set controllable to True if they do.
        """
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
    """
    Convience class for binary states.
    """

    BINARY_TYPE = 'binary'
    def __init__(self, category):
        super().__init__(category, [True, False], self.BINARY_TYPE)

class Trigger():
    """
    Functions to be called when a state transitions.
    """

    def __init__(self, category, state, func):
        self.key = uuid.uuid1()
        self.category = category
        self.state = state
        self.func = func

    def trigger(self):
        """
        Call the trigger.
        """
        self.func()

    def __eq__(self, other):
        if self.key == other.key:
            return True
        else:
            return False
