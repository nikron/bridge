"""
Test the cmds util mapping functionality.
"""
import unittest

from insteon.command.command_bytes_util import CMDS, CommandBytesMap

class TestCommandBytesUtil(unittest.TestCase):
    def setUp(self):
        self.cmd = CMDS(b'\x34', b'\x23')
        self.cmd2 = CMDS(b'\x34')
        self.cmd_map = CommandBytesMap(True)

    def test_cmd(self):
        self.assertEqual(hash(self.cmd), hash(b'\x34' + b'\x23'))

    def test_map(self):
        self.cmd_map.register(self.cmd, True)
        self.assertTrue(self.cmd_map.get(self.cmd))

    def test_raise(self):
        self.assertRaises(KeyError, self.cmd_map.get, self.cmd2)
