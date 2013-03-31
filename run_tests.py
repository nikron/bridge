#!/usr/bin/python3
import os.path
import unittest
import coverage

def main():
    this_dir = os.path.dirname(__file__)
    test_dir = os.path.join(os.path.abspath(this_dir), 'tests')

    cov = coverage.coverage(source=['bridge', 'insteon_protocol'])
    cov.start()
    suite = unittest.defaultTestLoader.discover(test_dir, pattern="*test.py")
    unittest.TextTestRunner(verbosity=2).run(suite)
    cov.stop()
    cov.save()
    cov.html_report()


if __name__ == "__main__":
    main()
