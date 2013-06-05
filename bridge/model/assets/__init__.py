"""
An asset is the internal representation of a device.
This file contains basic assets and the base class.
"""
from bridge.model.attributes import Attributes
from bridge.model.actions import Actions, action, get_actions
from bridge.services import BridgeMessage
import logging
import uuid

class Backing():
    """
    Backing strings and :class:`BridgeMessage`s of an Asset.
    """

    def __init__(self, real_id, service, product_name, **message_args):
        self.real_id = real_id
        self.service = service
        self.product_name = product_name
        self.bridge_messages = {}

        self.add_messages(**message_args)

    def add_messages(self, **message_args):
        """
        Create a list of messages out of keyword arguments.
        """
        for name in message_args:
            method, args = message_args[name]
            msg = BridgeMessage.create_async(self.service, method, self.real_id, *args)
            self.bridge_messages[name] = msg

    def get(self, name):
        """
        Get message of :arg:`name`.
        """
        return self.bridge_messages[name]

class Asset(metaclass = Actions):
    """
    Represent a physical device, such as a Keypadlinc.
    """

    def __init__(self, name, attributes, backing):
        self.name = name
        self.attributes = attributes
        self.backing = backing
        self.backing.add_messages(get_status = ('asset_info', []))

        self.uuid = uuid.uuid1()
        self.failed_changes = []

    def get_control_message(self, attribute, state):
        """
        Get the control message for a attribute and state.
        """
        return self.attributes.get_control(attribute, state)

    def get_product_name(self):
        """
        The product name of the asset ie ApplianceLinc V2
        """
        return self.backing.product_name

    def get_real_id(self):
        """
        Real id of asset, (usually a str, definately a str for insteon (instead of bytes))
        """
        return self.backing.real_id

    def get_service(self):
        """
        Get the service the asset belongs to.
        """
        return self.backing.service

    def serializable(self):
        """
        Return a form of the class that is easy to serialize (with JSON etc)
        """
        ser = {}
        ser['name'] = self.name
        ser['product'] = self.backing.product_name
        ser['uuid'] = self.uuid
        ser['real id'] = self.get_real_id()
        ser['actions'] = get_actions(self)
        ser['attributes'] =  self.attributes.serializable()

        return ser

    def change(self, attribute, state):
        """
        Change the state of an attribute to a state.
        """
        logging.debug("Going to state ({0}, {1})".format(attribute, state))
        return self.attributes.change(attribute, state)

    @action("Get Status")
    def get_status(self):
        """
        Uniform action of all assets, tries to get full status from IO.
        """
        return self.backing.bridge_messages['get_status']

    def _set_control_passthrough(self, attribute, service_method):
        """
        Sets a control function to simply call a method on an IO
        service named service_method.
        """
        func = lambda x : BridgeMessage.create_async(self.get_service(), service_method, self.get_real_id(), x)
        self.attributes.set_default_control(attribute, func)
