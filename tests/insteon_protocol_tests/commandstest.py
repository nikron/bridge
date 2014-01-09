import unittest

from insteon.command.commands import InsteonCommand

class TestInsteonCommand(unittest.TestCase):
    def test_command(self):
        cmd = InsteonCommand(b'\x00\x00\x00', b'\x00\x00\x00', False, False, False, False, 0, 0, b'\x00', b'\x00', b'')
        encd = cmd.encode()

        self.assertEquals(encd, b'\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        decd = InsteonCommand.decode(encd)
        self.assertFalse(decd.ack)
