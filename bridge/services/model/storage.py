"""
Drivers for storing the model to persistent storage.
"""
from bridge.services.model.model import Model

import os
import shutil
import json
import uuid

class ModelStorage():
    """Store and read model to a persistent state."""

    DEFAULT = "default.bridge"

    def __init__(self, directory):
        self.directory = directory
        self.data = os.path.abspath(os.path.join(self.directory, 'data'))
        self.last = os.path.abspath(os.path.join(self.directory, 'last'))
        self.file_name = os.path.abspath(os.path.join(self.data, self.DEFAULT))

        self.create_files()

        self.read_last()

    def create_files(self):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        if not os.path.exists(self.data):
            os.makedirs(self.data)

        if not os.path.exists(self.last):
            fd = open(self.last, "w")
            fd.close()
            

    def remove_files(self):
        shutil.rmtree(self.directory)

    def read_model(self, idioms, file_name = None):
        """Read the save model from the file."""
        file_name = self._make_file_name(file_name)

        self.write_last() #this is the last file name either way
        model = Model()

        try:
            fd = open(file_name, "r+")
            json_model = json.load(fd)

            for asset_dict in json_model['assets']:
                asset = idioms[asset_dict['service']].create_asset(asset_dict['name'], asset_dict['real id'], asset_dict['product name'])
                asset.uuid = uuid.UUID(asset_dict['uuid'])
                model.add_asset(asset)

            return model

        except FileNotFoundError:
            return model

        except ValueError:
            return model

    def write_model(self, model, file_name = None):
        """
        Write model to the file.
        Return if succesful or not.
        """
        file_name = self._make_file_name(file_name)

        with open(file_name, "w+") as fd:
            save_dict = {'assets' : []}

            for asset_uuid in model.get_all_asset_uuids():
                asset = model.get_asset(asset_uuid)
                save_dict['assets'].append({
                            'name' : asset.get_name(), 
                            'uuid' : str(asset_uuid), 
                            'real id' : asset.get_real_id(),
                            'service' : asset.get_service(),
                            'product name' : asset.get_product_name()
                            })

            json.dump(save_dict, fd, indent=4)
            self.write_last()
            return True

        return False

    def read_last(self):
        with open(self.last, 'r+') as fd:
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
            file_name = os.path.abspath(os.path.join(self.data, file_name))
            if os.path.dirname(file_name) != self.data:
                raise AttributeError('File does not stay within data directory.')

            self.file_name = file_name

            return  file_name

class PickleStorage(ModelStorage):
    DEFAULT = 'default.pickle'


