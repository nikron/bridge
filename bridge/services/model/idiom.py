"""An abstract base class for and io idiom.  Each type of io service 
(only insteon) must create an io idiom so the model can communicate with it"""

from abc import ABCMeta, abstractmethod

class ModelIdiom(metaclass=ABCMeta):
    @abstractmethod
    def guess_asset(self, update):
        pass

    @abstractmethod
    def get_state(self, update):
        pass
