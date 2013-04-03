#!/usr/bin/python3
import os.path
import unittest
try:
    import coverage
except ImportError:
    coverage = None

def main():
    this_dir = os.path.dirname(__file__)
    test_dir = os.path.join(os.path.abspath(this_dir), 'tests')

    if coverage:
        cov = coverage.coverage(source=['bridge', 'insteon_protocol'])
        cov.start()

    suite = unittest.defaultTestLoader.discover(test_dir, pattern="*test.py")
    unittest.TextTestRunner(verbosity=2).run(suite)

    if coverage:
        cov.stop()
        cov.save()
        cov.report()


if __name__ == "__main__":
    main()
