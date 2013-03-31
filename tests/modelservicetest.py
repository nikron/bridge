import unittest

from bridge.services.model.service import ModelService
from bridge.services.io.insteon.idiom import InsteonIdiom
from multiprocessing import Pipe

class TestModelService(unittest.TestCase):
    def setUp(self):
        idiom = InsteonIdiom('idiom')
        (self.ours, its) = Pipe()

        self.serv = ModelService({'idiom' : idiom}, 'none', 'none', its)

    def test_service_info(self):
        self.assertEquals(self.serv.get_services(), ['idiom'])
        self.serv.io_service_online('idiom')

        self.assertTrue(self.serv.get_service_info('idiom')['online'])
