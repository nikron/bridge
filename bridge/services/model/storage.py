"""
Read and write a model to disk.
"""
from bridge.model import Model

import os
import shutil
import json
import uuid

class ModelStorage():
    """
    Store and read model to storage.

    :param directory: Directory to use to save models.
    :type directory: str
    """

    DEFAULT = "default.bridge"

    def __init__(self, directory):
        self.directory = directory
        self.data = os.path.abspath(os.path.join(self.directory, 'data'))
        self.last = os.path.abspath(os.path.join(self.directory, 'last'))
        self.file_name = os.path.abspath(os.path.join(self.data, self.DEFAULT))

        self._create_files()

        self._read_last()

    def get_current_file(self):
        """
        :return: The current file used for storing a Model
        :rtype: str
        """
        return self.file_name

    def get_files(self):
        """
        :return:  All files inside the storage directory.
        :rtype: list
        """
        return os.listdir(self.data)

    def read_model(self, idioms, file_name = None):
        """
        Read model from file, stored as a JSON dict with enough information
        for an idiom to recreate it.

        :param idioms: Dicitionary of idioms to use to recreate the model.
        :type model: dict

        :param file_name: The path to write the model from, if none use last or default path.
        :type file_name: str

        :return: Returns a model, an empty model (not None) if it not able to read file.
        :rtype: Model
        """
        file_name = self._make_file_name(file_name)

        self._write_last()
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

    def remove_files(self):
        """
        Remove the file tree that the storage needs.
        Mostly used for testing.
        """
        shutil.rmtree(self.directory)

    def write_model(self, model, file_name = None):
        """
        Write model to the file, storing information the minimum information an idiom would need
        to recreate it.

        :param model: The model to write to disk
        :type model: Model

        :param file_name: The path to write the model to, if none use last or default path.
        :type file_name: str

        :return: Returns if the operation was successful
        :rtype: bool
        """
        file_name = self._make_file_name(file_name)

        with open(file_name, 'w+') as fd:
            save_dict = {'assets' : []}

            for asset_uuid in model.get_all_asset_uuids():
                asset = model.get_asset(asset_uuid)
                save_dict['assets'].append({
                            'name' : asset.name,
                            'uuid' : str(asset_uuid),
                            'real id' : asset.get_real_id(),
                            'service' : asset.get_service(),
                            'product name' : asset.get_product_name()
                            })

            json.dump(save_dict, fd, indent=4)
            self._write_last()
            return True

        return False

    def _create_files(self):
        """
        Create the files this classes needs if they do not exist inside its assigned directory.
        """
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        if not os.path.exists(self.data):
            os.makedirs(self.data)

        if not os.path.exists(self.last):
            fd = open(self.last, "w")
            fd.close()

    def _make_file_name(self, file_name):
        """
        Make the current file name file_name if it is not None.

        :param file_name: Path to save file.
        :type file_name: str
        """
        if file_name is None:
            return self.file_name

        else:
            file_name = os.path.abspath(os.path.join(self.data, file_name))
            if os.path.dirname(file_name) != self.data:
                raise AttributeError('File does not stay within data directory.')

            self.file_name = file_name

            return  file_name

    def _read_last(self):
        """
        Read the last used saved file to disk, so we can use it next time.
        """
        with open(self.last, 'r+') as fd:
            self.file_name = fd.readline()

        if self.file_name == '':
            self.file_name = os.path.join(self.data, self.DEFAULT)

    def _write_last(self):
        """
        Write the last used saved file to disk, so we can use it next time.
        """
        with open(self.last, 'w+') as fd:
            fd.write(self.file_name)
