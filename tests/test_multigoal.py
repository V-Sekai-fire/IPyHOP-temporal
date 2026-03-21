#!/usr/bin/env python
"""
Tests for MultiGoal class.

Covers multi-goal handling and goal achievement checking.
"""

import unittest
import sys
import os
import importlib.util

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import directly to avoid matplotlib dependency
mg_spec = importlib.util.spec_from_file_location("multigoal", "ipyhop/multigoal.py")
mg_module = importlib.util.module_from_spec(mg_spec)
mg_spec.loader.exec_module(mg_module)
MultiGoal = mg_module.MultiGoal

state_spec = importlib.util.spec_from_file_location("state", "ipyhop/state.py")
state_module = importlib.util.module_from_spec(state_spec)
state_spec.loader.exec_module(state_module)
State = state_module.State


class TestMultiGoal(unittest.TestCase):
    """Test MultiGoal class."""
    
    def test_initialization(self):
        """Test MultiGoal initialization."""
        mg = MultiGoal('test_mg')
        self.assertIsNotNone(mg)
        self.assertEqual(mg.goal_tag, None)
        self.assertEqual(mg.__name__, 'test_mg')
    
    def test_initialization_with_tag(self):
        """Test MultiGoal initialization with goal tag."""
        mg = MultiGoal('test_mg', 'my_tag')
        self.assertEqual(mg.goal_tag, 'my_tag')
    
    def test_goal_assignment(self):
        """Test assigning goals to MultiGoal."""
        mg = MultiGoal('test_mg')
        mg.loc = {'obj1': 'room1', 'obj2': 'room2'}
        self.assertEqual(mg.loc['obj1'], 'room1')
        self.assertEqual(mg.loc['obj2'], 'room2')
    
    def test_multiple_goal_types(self):
        """Test assigning multiple goal types."""
        mg = MultiGoal('test_mg')
        mg.loc = {'obj1': 'room1'}
        mg.status = {'obj1': 'active'}
        self.assertEqual(mg.loc['obj1'], 'room1')
        self.assertEqual(mg.status['obj1'], 'active')
    
    def test_goal_update(self):
        """Test updating MultiGoal."""
        mg1 = MultiGoal('mg1')
        mg1.loc = {'obj1': 'room1'}
        
        mg2 = MultiGoal('mg2')
        mg2.loc = {'obj2': 'room2'}
        
        # update() replaces __dict__, so mg1.loc becomes mg2.loc
        mg1.update(mg2)
        # After update, mg1.loc should be replaced with mg2.loc
        self.assertEqual(mg1.loc, {'obj2': 'room2'})
    
    def test_goal_copy(self):
        """Test copying MultiGoal."""
        mg = MultiGoal('test_mg')
        mg.loc = {'obj1': 'room1'}
        mg_copy = mg.copy()
        self.assertEqual(mg_copy.loc['obj1'], 'room1')
        # Modify copy
        mg_copy.loc['obj2'] = 'room2'
        self.assertNotIn('obj2', mg.loc)
    
    def test_string_representation(self):
        """Test string representation."""
        mg = MultiGoal('test_mg')
        mg.loc = {'obj1': 'room1'}
        str_repr = str(mg)
        self.assertIn('test_mg', str_repr)
        self.assertIn('loc', str_repr)


if __name__ == '__main__':
    unittest.main()
