"""
An abstract base class for an io idiom.  Each type of io service must subclass
this and give to the ModelService at start time to communicate with it.
"""

from abc import ABCMeta, abstractmethod

class ModelIdiom(metaclass = ABCMeta):
    """
    ModelService uses this class to figure out what an IO update means.

    :param service: The service name (not type) that this idiom deciphers.
    :type service: str
    """

    def __init__(self, service):
        self.service = service
        self.online = False

    @abstractmethod
    def create_asset(self, name, real_id, product_name):
        """
        Create an asset with real_id.
        The idiom should be able to glean enough information from the user supplied product name to create
        an asset that models the device.

        :param name: The name of the asset that the user sees.
        :type name: str

        :param real_id: The ID that the IO service uses.
        :type real_id: object

        :param product_name: The product name of the device.
        :type product_name: str

        :return: The initialiazed asset.
        :rtype: Asset
        """
        pass

    @abstractmethod
    def change_state(self, asset, update):
        """
        Change the state of an asset using an update supplied by the IO service
        linked to this idiom.

        :param asset: The asset to change.
        :type asset: Asset

        :param update: An update that came from the linked IO service.
        :type update: object
        """
        pass

    @abstractmethod
    def guess_asset(self, real_id, update):
        """
        If the Model Service gets an update from a device from an asset it does not know
        about, it asks to best guess the asset.

        :param real_id: The ID that the IO service uses.
        :type real_id: object

        :param update: An arbitrary update from the linked IO service.
        :param update: object

        :return: A tuple of the asset and a boolean, where the boolean is if the asset is known to be correct.
        :rtype: (Asset, bool)
        """
        pass

    @abstractmethod
    def product_names(self):
        """
        Return list of strings of accepted asset types.
        """
        pass

class IdiomError(Exception):
    """
    Idiom errors.

    :param reason: The reason for the error.
    :type reason: str
    """
    def __init__(self, reason):
        super().__init__()
        self.reason = reason

    def __str__(self):
        return self.reason
