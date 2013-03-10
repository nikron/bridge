import unittest

"""Test Case Example
File in which to hold related tests.
To be seen by the test runner, import the class in __init__.py in the testrunner module folder.
"""
class ExampleTestCase(unittest.TestCase):

	def setUp(self): 
		return True

	"""Example test
	All tests must be prepended with "test" to be recognized by the testrunner
	Helper method (such as setUp) will not be listed.
	"""
	def testSomething(self):
		return True


