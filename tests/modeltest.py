"""
Test the model.
"""
import unittest
from bridge.model import Model
from bridge.model.assets.basic_assets import BlankAsset

class TestModel(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.model.add_service('upb')
        self.asset = BlankAsset('blah', 'upb')
        self.model.add_asset(self.asset)

    def test_get(self):
        uuid = self.model.get_asset_uuid('upb', 'blah')
        asset = self.model.get_asset(uuid)

        self.assertIs(asset, self.asset)

    def test_serializable(self):
        uuid = self.model.get_asset_uuid('upb', 'blah')
        info = self.model.serializable_asset_info(uuid)

        self.assertEqual(info['product'], '')
        self.assertEqual(info['name'], '')
