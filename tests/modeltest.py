import unittest
from bridge.services.model.model import Model
from bridge.services.model.assets import BlankAsset

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
        self.assertEqual(self.model.get_all_asset_names(), [""])

    def test_serializable(self):
        uuid = self.model.get_asset_uuid('upb', 'blah')
        info = self.model.serializable_asset_info(uuid)

        self.assertEqual(info['asset type'], 'BlankAsset')
        self.assertEqual(info['name'], '')
