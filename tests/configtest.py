import tempfile

import unittest

from bridge.config import BridgeConfiguration

class TestBridgeConfig(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.NamedTemporaryFile()
        self.temp.write(
b"""[general]
;path name
log = {this_dir}/bridge.log

[model]
;file the model stores its information in
file = {this_dir}/.model
driver = none

[io]
services = insteon

[insteon]
name = insteon
protocol = insteon
file name = /dev/ttyUSB0
""")
        self.temp.flush()

    def test_config(self):
        config = BridgeConfiguration(self.temp.name, False)

        self.assertFalse(config.stderr)
        self.assertEqual(config.model_driver, 'none')
        self.assertEqual(config.io_services, [('insteon', 'insteon','/dev/ttyUSB0')])
