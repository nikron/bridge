import unittest

from insteon.insteon_exception import InsteonException

class TestInsteonCommand(unittest.TestCase):
    def test_command(self):
        def raiseException():
            raise InsteonException("hey")

        self.assertRaises(InsteonException, raiseException)
