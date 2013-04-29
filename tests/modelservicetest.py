"""
Test the model service.
"""
import unittest

from bridge.services.model.service import ModelService
from bridge.services.io.insteon.idiom import InsteonIdiom
from multiprocessing import Pipe

class TestModelService(unittest.TestCase):
    def setUp(self):
        idiom = InsteonIdiom('idiom')
        (self.ours, its) = Pipe()

        self.serv = ModelService({'idiom' : idiom}, 'none', its)

    def test_service_info(self):
        self.assertEquals(self.serv.get_io_services(), ['idiom'])
        self.serv.io_service_online('idiom')

        self.assertTrue(self.serv.get_io_service_info('idiom')['online'])

        self.serv.storage.remove_files()
