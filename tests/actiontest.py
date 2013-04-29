"""
Test actions, by making a class with it as a metaclass
and performing the action.
"""
import unittest
from bridge.services.model.actions import Actions, action, perform_action

class TestActions(unittest.TestCase):
    def setUp(self):
        class innerAction(metaclass = Actions):
            def __init__(self):
                self.x = False

            @action("Flip the bit.")
            def floop(self):
                self.x = True

        self.inner = innerAction()


    def test_action(self):
        perform_action(self.inner, 'floop')
        self.assertTrue(self.inner.x)

