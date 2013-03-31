import unittest
from bridge.services.model.model import Model
from bridge.services.model.assets import BlankAsset

class TestModel(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.model.add_service('upb')
        self.asset = BlankAsset('blah')
        self.model.add_asset('upb', self.asset)

    def test_get(self):
        uuid = self.model.get_uuid('upb', 'blah')
        asset = self.model.get_asset(uuid)

        self.assertIs(asset, self.asset)
        self.assertEqual(self.model.get_all_asset_names(), [""])
