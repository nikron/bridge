import unittest

from bridge.services.model.model import Model
from bridge.services.model.storage import get_storage, NoneStorage

class TestStorage(unittest.TestCase):
    def test_none(self):
        store = get_storage('none file', 'none')
        self.assertIsInstance(store, NoneStorage)
        self.assertIsInstance(store.read_saved_model(), Model)
