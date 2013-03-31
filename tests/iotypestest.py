import unittest
from bridge.services.io.types import IOConfig
from bridge.services.io.insteon.idiom import InsteonIdiom

class TestIOConfig(unittest.TestCase):
    def setUp(self):
        self.io_config = IOConfig('insteon!1', 'insteon', 'whatever')

    def test_create(self):
        io_service = self.io_config.create_service(None)

        self.assertEquals(io_service.name, "insteon!1")

    def test_model(self):
        idiom = self.io_config.model_idiom()
        self.assertIsInstance(idiom, InsteonIdiom)
