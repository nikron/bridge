from abc import ABCMeta, abstractmethod
from .model import Model

import logging

def get_storage(file_name, driver):
    drivers = { 'none' : NoneStorage }

    try:
        return drivers[driver](file_name)

    except KeyError:
        logging.error("Could not find the " + driver + " driver for model, using none.")
        return drivers['none'](file_name)


class ModelStorage():
    __metaclass__ =ABCMeta #temporary so pylint can scan file

    def __init__(self, file_name):
        self.fd = open(file_name, 'rw')

    @abstractmethod
    def read_saved_model(self):
        pass

    @abstractmethod
    def write_model(self, model): 
        pass

class NoneStorage(ModelStorage):
    def __init__(self, file_name):
        #don't open the file
        pass

    def read_saved_model(self):
        return  Model()

    def write_model(self, model):
        #do nothing
        pass
