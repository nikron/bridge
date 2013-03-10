import unittest
import sys
import inspect

from tests import *

class TestRunner(unittest.TextTestRunner):

	testCases = []

	def __init__(self):
		super(TestRunner, self).__init__(verbosity=2)

	def gatherTestCases(self):
		#Finds all subclasses of unittest.TestCase
		self.testCases = [cls for name, cls in inspect.getmembers(sys.modules[__name__]) if inspect.isclass(cls) and issubclass(cls, unittest.TestCase)]

	def printTestCases(self):
		print("0 : AllTests")
		i = 1
		for t in self.testCases:
			print(str(i)+" : "+t.__name__)
			i += 1
		print("-1 : Exit")

	def runTestCase(self, testCase):
		print("\nRunning "+testCase.__name__)
		print("----------------------------------------------------------------------")
		self.run(unittest.makeSuite(testCase,'test'))

	def runTestCaseByIndex(self, index):
		if index == 0:
			self.runAllTests()
		else:
			self.runTestCase(self.testCases[index-1])

	def runAllTests(self):
		for t in self.testCases:
			self.runTestCase(t)


def main():
	running = True
	runner = TestRunner()
	runner.gatherTestCases()

	while(running):
		print("Select Test Case To Run")
		runner.printTestCases()
		valid = False
		try:
			val = int(input())
			valid = True
		except ValueError:
			print("That's not an int!")
		if val < 0:
			running = False
		if running and valid:
			runner.runTestCaseByIndex(val)

if __name__ == "__main__":
	main()