"""
Test loading a configuration, write one to a temp file and then
attempt to parse it.
"""
import tempfile

import unittest

from bridge.config import BridgeConfiguration
from bridge.hub import BridgeHub

class TestBridgeCore(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.NamedTemporaryFile()
        self.temp.write(
b"""[general]
;path name
log = {this_dir}/bridge.log
dir = {this_dir}/.bridge

[io]
services = insteon

[insteon]
name = insteon
protocol = insteon
file name = /dev/ttyUSB0
""")
        self.temp.flush()
        self.config = BridgeConfiguration(self.temp.name, False)

    def test_config(self):
        self.assertFalse(self.config.stderr)
        self.assertEqual(self.config.io_services, [('insteon', 'insteon','/dev/ttyUSB0')])

    def test_hub(self):
        self.assertIsNotNone(BridgeHub(self.config))
