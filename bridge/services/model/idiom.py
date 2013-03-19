"""An abstract base class for and io idiom.  Each type of io service 
(only insteon) must create an io idiom so the model can communicate with it"""

from abc import ABCMeta, abstractmethod

class ModelIdiom(metaclass=ABCMeta):
    """
    ModelService uses this class to figure out what an IO update means.
    """

    def __init__(self, service):
        self.service = service
        self.service_function = None

    @abstractmethod
    def create_asset(self, name, real_id, asset_type):
        """
        Create an asset with real_id
        """
        pass

    @abstractmethod
    def guess_asset(self, real_id, update):
        """
        Guess an asset class with the update package the corresponding service
        provide.  Then create and return a tuple (asset, positive) where
        positive is if the asset is exactly the correct one for the
        update.
        """
        pass

    @abstractmethod
    def get_state(self, real_id, update):
        """
        Get the state an asset should transition to if it is the
        correct asset.
        """
        pass

    @abstractmethod
    def asset_types(self):
        """
        Return list of strings of accepted asset types.
        """
        pass

    def charge(self, func):
        """
        Charge the idiom with a function that creates functions that
        communicate with service.
        """
        self.service_function = func
