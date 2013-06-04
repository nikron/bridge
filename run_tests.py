#!/usr/bin/python3
import os.path
import unittest
import argparse
import logging
try:
    import coverage
except ImportError:
    coverage = None

def parse_opts():
    parser = argparse.ArgumentParser(description='bridge tests')
    parser.add_argument('-c', '--coverage', help='Run coverage too', action='store_true')

    opts = parser.parse_args()

    return opts

def main():
    opts = parse_opts()

    this_dir = os.path.dirname(__file__)
    test_dir = os.path.join(os.path.abspath(this_dir), 'tests')

    root = logging.getLogger()
    root.setLevel(logging.CRITICAL)

    if opts.coverage and coverage:
        cov = coverage.coverage(source=['bridge', 'insteon_protocol', 'upb'])
        cov.start()

    suite = unittest.defaultTestLoader.discover(test_dir, pattern="*test.py")
    unittest.TextTestRunner(verbosity=2).run(suite)

    if opts.coverage and coverage:
        cov.stop()
        cov.save()
        cov.report()


if __name__ == "__main__":
    main()
