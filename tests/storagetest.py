import unittest
import os

from bridge.services.model.model import Model
from bridge.services.model.storage import get_storage, NoneStorage

class TestStorage(unittest.TestCase):
    def setUp(self):
        self.store = get_storage('none file', 'none')

    def test_none(self):
        self.assertIsInstance(self.store, NoneStorage)
        self.assertIsInstance(self.store.read_model('none'), Model)


    def test_remove(self):
        self.store.remove_files()
        self.assertFalse(os.path.exists('none file'))

