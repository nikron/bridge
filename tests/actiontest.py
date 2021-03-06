"""
Test actions, by making a class with it as a metaclass
and performing the action.
"""
import unittest
from bridge.model.actions import Actions, action, perform_action, get_actions, get_action_information

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

    def test_get_actions(self):
        acts = get_actions(self.inner)
        self.assertEquals(['floop'], acts)

    def test_get_action(self):
        act = get_action_information(self.inner, 'floop')
        self.assertEquals(act['name'], 'Flip the bit.')
