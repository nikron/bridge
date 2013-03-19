#!/usr/bin/python3
import os.path
import tests
import unittest

def main():
    this_dir = os.path.dirname(__file__)
    test_dir = os.path.join(os.path.abspath(this_dir), 'tests')

    suite = unittest.defaultTestLoader.discover(test_dir, pattern="*test.py")
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == "__main__":
    main()
