import unittest
import os

from bridge.services.model.model import Model
from bridge.services.model.storage import ModelStorage

class TestStorage(unittest.TestCase):
    def setUp(self):
        self.store = ModelStorage('none dir')

    def test_none(self):
        self.assertIsInstance(self.store.read_model('none'), Model)

    def test_remove(self):
        self.store.remove_files()
        self.assertFalse(os.path.exists('none file'))

