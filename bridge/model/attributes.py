"""
Meant to hold the status/state/attributes of a device. Anything that will
change on a device and should be controlled is considered a state. Examples:
lighting, volume, and status of LED buttons.
"""

class Attributes(dict):
    """
    A collection of independent :class:`Attributes`s.  A attribute is meant to
    be changed by transition of a category of attribute to another state.
    Another important function of an attribute is the notion of whether it is
    "controllable", it is considered controllable if all of its possible
    states have a control object associated with it.

    :param *states: List of :class:`Attribute`(s)
    :type *states: [:class:`Attribute`]
    """
    def __init__(self, *attributes):
        super().__init__()
        self.add(*attributes)

    def add(self, *attributes):
        for attribute in attributes:
            self[attribute.name] = attribute

    def change(self, attribute, state):
        """
        Attempt to transition a attribute to a particular state.

        :param attribute: The category name to change.
        :type attribute: str

        :param state: The state to transition to.
        :type state: str

        :return: Whether the transition was successful.
        :rtype: bool
        """
        if attribute not in self:
            return False

        return self[attribute].change(state)

    def get_control(self, attribute, state):
        """
        Get a control object from an attribute for a state.  This object
        is intended to be a :class:`BridgeMessage`that allows for control of the device.

        :param attribute: The attribute name to get the control object.
        :type attribute: str

        :param state: The state of an attribute that the object controls.
        :type state: str

        :return: The control object associated with changing to a state.
        :rtype: object
        """
        return self[attribute].get_control(state)

    def serializable(self):
        """
        Return a representation of the :class:`States` in a form of only
        Python primitives, one that is easy to serialize.

        :return: The serilizable dictionary representing this :class:`States`.
        :rtype: dict
        """
        ser = {}

        for attribute in self.keys():
            ser[attribute] = self[attribute].serializable()

        return ser

    def set_default_control(self, attribute, control):
        """
        Set a callable object on an attribute, the object will be called
        with the target state and the result will be returned when
        :func:`get_control`.

        :param category: The attribute name to get the control object.
        :type category: str

        :param param: The control object
        :type object:
        """
        self[attribute].set_default_control(control)

    def set_control(self, attribute, state, control):
        """
        Set an object to be returned on :func:`get_control`, if a
        :class:`Attribute`'s all possible states have control objects,
        that :class:`Attribute` will be considered controllable.

        :param attribute: The attribute name to get set control object.
        :type attribute: str

        :param state: The state that the object controls.
        :type state: str

        :param param: The control object
        :type object:
        """
        self[attribute].set_control(state, control)

class Attribute():
    """
    Aategory of states, keeps track of various attributes of state, most
    of important of which are whether it is "controllable", and whether the
    current state is "known".

    :param name: The name of the attribute
    :type name: str

    :param states: An object with the __contains__ method defined.
    :type states: object

    :param _type: The type of category it is, intended for clients to know
                  what kind of control to display for this state
    :type _type: str
    """
    def __init__(self, name, states, _type):
        self.name = name
        self.states = states
        self.type = _type

        self.current_state = None
        self.unknown = True
        self.controllable = False
        self.default_control = None

        self.controls = {}

    def change(self, state):
        """
        Makes the current state to be another state.

        :param state: State to transition to.
        :type state: str
        """
        if state in self.states:
            self.current_state = state

            self.set_unknown(False)
            return True

        else: return False

    def get_name(self):
        """
        :return: The name of states that this object represents.
        :rtype: str
        """
        return self.name

    def get_control(self, state):
        """
        Return an object that is used to change this attribute to a state. If
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

    def serializable(self):
        """
        :return: Return a form of this category easy to serialize.
        :rtype: dict
        """
        ser = {}
        ser['current'] = self.serialize_current_state()
        ser['type'] = self.type
        ser['controllable'] = self.controllable
        ser['unknown'] = self.unknown
        ser['possible'] = self.serialize_possible_states()

        return ser

    def serialize_current_state(self):
        return self.current_state

    def serialize_possible_states(self):
        return self.states

    def set_control(self, state, control):
        """
        Set the control object for a state, make it controllable if all
        possible states have controls.

        :param state: State to set control to
        :type state: str

        :param control: Control to change the state.
        :type control: object
        """
        self.controls[state] = control
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
        if it is unknown is False.

        :param unknown: If the current state is known or not.
        :type unknown: bool
        """
        if unknown:
            self.current_state = None

        self.unknown = unknown

    @staticmethod
    def deserialize_current_state(possible_rep, state):
        if state in possible_rep:
            return state
        else:
            return None

    def _check_controllable(self):
        """
        Check if all the possible states have a control object associated with
        them, set controllable to True if they do.
        """
        if self.default_control:
            self.controllable = True
        else:
            self.controllable = True
            try:
                for state in self.states:
                    if state not in self.controls:
                        self.controllable = False
                        return
            except TypeError:
                self.controllable = False

    def __contains__(self, state):
        return state in self.states

    def __eq__(self, other):
        return self.name.__eq__(other.name)

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name

class BinaryAttribute(Attribute):
    """
    Convience class for binary states.
    """

    def __init__(self, category):
        super().__init__(category, [True, False], BINARY_TYPE)

class IntegerAttribute(Attribute):
    """
    Convience class for a range of states.
    """

    def __init__(self, category, minimum, maximum, step = 1):
        super().__init__(category, range(minimum, maximum, step), INT_TYPE)

    def serialize_possible_states(self):
        return '{0}:{1}:{2}'.format(self.states.start, self.states.stop, self.states.step)

    @staticmethod
    def deserialize_current_state(possible_rep, state):
        start, stop, step = [int(num) for num in possible_rep.split(':')]
        if state in range(start, stop, step):
            return state
        else:
            return None

class ByteAttribute(IntegerAttribute):
    def __init__(self, category):
        super().__init__(category, 0, 256)

class BytesWrapper():
    def __init__(self, max_length):
        self.max = max_length

    def serializable(self):
        return self.max

    def __contains__(self, obj):
        if isinstance(obj, bytes) and len(obj) <= self.max:
            return True
        else:
            return False

class ASCIIAttribute(Attribute):
    def __init__(self, category, length):
        super().__init__(category, BytesWrapper(length), ASCII_TYPE)

    def serialize_current_state(self):
        if self.current_state:
            return self.current_state.decode()
        else:
            return self.current_state

    def serialize_possible_states(self):
        return self.states.max

    @staticmethod
    def deserialize_current_state(possible_rep, state):
        if isinstance(state, str):
            bytes_string = state.encode()
            if len(bytes_string) <= possible_rep:
                return bytes_string

        return None

BINARY_TYPE = 'binary'
INT_TYPE = 'integer'
ASCII_TYPE = 'ascii'

ATTRIBUTE_TYPES = {
        BINARY_TYPE : BinaryAttribute,
        INT_TYPE : IntegerAttribute,
        ASCII_TYPE :  ASCIIAttribute
        }

def verify_state(attr_serializable, state):
    cls = ATTRIBUTE_TYPES[attr_serializable['type']]
    possible_rep = attr_serializable['possible']
    return cls.deserialize_current_state(possible_rep, state)
