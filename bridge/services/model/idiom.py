"""An abstract base class for and io idiom.  Each type of io service 
(only insteon) must create an io idiom so the model can communicate with it"""

from abc import ABCMeta, abstractmethod

class ModelIdiom():
    """
    ModelService uses this class to figure out what an IO update means.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def guess_asset(self, update):
        """
        Guess an asset class with the update package the corresponding service
        provide.  Then create and return a tuple (asset, positive) where
        positive is if the asset is exactly the correct one for the
        update.
        """
        pass

    @abstractmethod
    def get_state(self, update):
        """
        Get the state an asset should transition to if it is the
        correct asset.
        """
        pass
