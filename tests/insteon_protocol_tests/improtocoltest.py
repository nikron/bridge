import io
import unittest

from insteon.insteon_im_protocol import read_command, decode

class TestIMProtocol(unittest.TestCase):
    def setUp(self):
        self.cmd1 = b'\x02b\x00\xf1\xd1\x0f\x13\x00\x06'
        self.cmd2 = b'\x02P\x00\xf1\xd1 \xf5U+\x13\x00'
        self.cmd3 = b'\x02b\x00\xf1\xd1\x1f\x03\x03Tis was a pony\x06'

        self.tmp = io.BytesIO(self.cmd1 + self.cmd2 + self.cmd3)

    def test_read_command(self):
        buf = read_command(self.tmp)
        self.assertEquals(self.cmd1, buf)
        buf = read_command(self.tmp)
        self.assertEquals(self.cmd2, buf)
        buf = read_command(self.tmp)
        self.assertEquals(self.cmd3, buf)
        buf = read_command(self.tmp)
        self.assertIsNone(buf)


    def test_decode(self):
       buf = b'asdfasdf'
       self.assertIsNone(decode(buf))

       self.assertIsNotNone(decode(self.cmd1))
