"""
Drivers for storing the model to persistent storage.
"""
from bridge.services.model.model import Model
import os
import shutil

import logging
import pickle

class ModelStorage():
    """Store and read model to a persistent state."""

    DEFAULT = "default.bridge"

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

    def read_model(self, file_name = None):
        """Read the save model from the file."""
        file_name = self._make_file_name(file_name)

        self.write_last() #this is the last file name either way
        with open(file_name, "wb+") as fd:
            try:
                model = pickle.load(fd)
                if type(model).__name__ == "Model":
                    return model
            finally:
                return Model()

        return Model()

    def write_model(self, model, file_name = None):
        """
        Write model to the file.
        Return if succesful or not.
        """
        file_name = self._make_file_name(file_name)

        with open(file_name, "wb+") as fd:
            pickle.dump(model, fd)
            self.write_last()
            return True

        return False

    def read_last(self):
        with open(self.last, 'w+') as fd:
            self.file_name = fd.readline()

        if self.file_name == '':
            self.file_name = os.path.join(self.data, self.DEFAULT)
    
    def write_last(self):
        with open(self.last, 'w+') as fd:
            fd.write(self.file_name)

    def _make_file_name(self, file_name):
        if file_name is None:
            return self.file_name

        else:
            file_name = os.path.join(self.data, file_name)
            if os.path.dirname(file_name) != self.data:
                raise AttributeError('File does not stay within data directory.')

            self.file_name = file_name

            return  file_name

class PickleStorage(ModelStorage):
    DEFAULT = 'default.pickle'


