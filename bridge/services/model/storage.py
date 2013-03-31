"""
Drivers for storing the model to persistent storage.
"""
from abc import ABCMeta, abstractmethod
from bridge.services.model.model import Model

import logging

def get_storage(file_name, driver):
    """Retrieve storage class based on string."""
    drivers = { 'none' : NoneStorage }

    try:
        return drivers[driver](file_name)

    except KeyError:
        logging.error("Could not find the " + driver + " driver for model, using none.")
        return drivers['none'](file_name)


class ModelStorage(metaclass = ABCMeta):
    """Store and read model to a persistent state."""

    def __init__(self, file_name):
        self.file_name = file_name

    @abstractmethod
    def read_saved_model(self):
        """Read the save model from the file."""
        pass

    @abstractmethod
    def write_model(self, model):
        """Write model to the file."""
        pass

class NoneStorage(ModelStorage):
    """Don't store the model."""
    def __init__(self, file_name):
        pass

    def read_saved_model(self):
        """Create an empty model."""
        return Model()

    def write_model(self, model):
        """Don't save anything."""
        pass
