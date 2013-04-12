"""
Drivers for storing the model to persistent storage.
"""
from abc import ABCMeta, abstractmethod
from bridge.services.model.model import Model
import os
import shutil

import logging
import pickle

def get_storage(directory, driver):
    """Retrieve storage class based on string."""
    drivers = {
            'none' : NoneStorage,
            'pickle' : PickleStorage
            }

    try:
        return drivers[driver](directory)

    except KeyError:
        logging.error("Could not find the " + driver + " driver for model, using none.")
        return drivers['none'](directory)

def record_last(func):
    def inner(self, file_name=None, *args):
        if file_name == '':
            file_name = self.file_name

        elif file_name:
            file_name = os.path.join(self.data, file_name)
            if os.path.dirname(file_name) != self.data:
                raise AttributeError('File does not stay within data directory.')

        else:
            file_name = self.file_name

        ret = func(self, file_name, *args)

        if ret:
            self.write_last()

        return ret

    return inner

class ModelStorage(metaclass = ABCMeta):
    """Store and read model to a persistent state."""

    DEFAULT = "default"

    def __init__(self, directory):
        self.directory = directory
        self.data = os.path.join(self.directory, 'data')
        self.last = os.path.join(self.directory, 'last')
        self.file_name = os.path.join(self.data, self.DEFAULT)

        self.create_files()

        self.read_last()

    def create_files(self):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        if not os.path.exists(self.data):
            os.makedirs(self.data)
    
    def remove_files(self):
        shutil.rmtree(self.directory)

    @abstractmethod
    def read_model(self, file_name = None):
        """Read the save model from the file."""
        pass

    @abstractmethod
    def write_model(self, model, file_name = None):
        """
        Write model to the file.
        Return if succesful or not.
        """
        pass

    def read_last(self):
        with open(self.last, 'w+') as fd:
            self.file_name = fd.readline()

        if self.file_name == '':
            self.file_name = os.path.join(self.data, self.DEFAULT)
    
    def write_last(self):
        with open(self.last, 'w+') as fd:
            fd.write(self.file_name)


class NoneStorage(ModelStorage):
    """Don't store the model."""
    def read_model(self, file_name = None):
        """Create an empty model."""
        return Model()

    def write_model(self, model, file_name = None):
        """Don't save anything."""
        return False

class PickleStorage(ModelStorage):
    DEFAULT = 'default.pickle'

    @record_last
    def read_model(self, file_name):
        with open(file_name, "wb+") as fd:
            try:
                model = pickle.load(fd)
                if type(model).__name__ == "Model":
                    return model
            finally:
                return Model()

        return Model()

    @record_last
    def write_model(self, model, file_name):
        with open(file_name, "wb+") as fd:
            pickle.dump(model, fd)
            return True

        return False
