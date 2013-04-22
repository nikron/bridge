import unittest
import os

from bridge.services.model.model import Model
from bridge.services.io.insteon.idiom import InsteonIdiom
from bridge.services.model.storage import ModelStorage
from bridge.services.model.assets import BlankAsset, OnOffAsset

class TestStorage(unittest.TestCase):
    def setUp(self):
        self.store = ModelStorage('none dir')
        self.model = Model()
        self.idiom = InsteonIdiom('test')
        self.model.add_asset(self.idiom.create_asset('test', 'aaaaaa', 'ApplianceLinc V2'))

    def test_none(self):
        self.assertIsInstance(self.store.read_model('none'), Model)
        self.store.remove_files()

    def test_store(self):
        self.store.write_model(self.model, 'hmm')
        test = self.store.read_model({'test' : self.idiom}, 'hmm')
        self.assertEquals(test.get_asset(test.get_all_asset_uuids()[0]).get_service(), 'test')
        self.store.remove_files()

    def test_remove(self):
        self.store.remove_files()
        self.assertFalse(os.path.exists('none file'))

