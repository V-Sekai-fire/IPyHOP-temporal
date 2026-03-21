#!/usr/bin/env python
"""
Tests for Simple Temporal Network (STN).

Covers temporal constraint network operations.
"""

import unittest
import sys
import os
import importlib.util

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import directly to avoid matplotlib dependency
stn_spec = importlib.util.spec_from_file_location("stn", "ipyhop/temporal/stn.py")
stn_module = importlib.util.module_from_spec(stn_spec)
stn_spec.loader.exec_module(stn_module)
STN = stn_module.STN


class TestSTN(unittest.TestCase):
    """Test Simple Temporal Network."""
    
    def test_initialization(self):
        """Test STN initialization."""
        stn = STN()
        self.assertIsNotNone(stn)
        self.assertEqual(len(stn.time_points), 0)
        self.assertEqual(len(stn.constraints), 0)
        self.assertEqual(stn.time_unit, "second")
    
    def test_initialization_with_time_unit(self):
        """Test STN initialization with custom time unit."""
        stn = STN(time_unit="minute")
        self.assertEqual(stn.time_unit, "minute")
    
    def test_add_time_point(self):
        """Test adding time points to STN."""
        stn = STN()
        stn.add_time_point('A')
        stn.add_time_point('B')
        self.assertIn('A', stn.time_points)
        self.assertIn('B', stn.time_points)
        self.assertEqual(len(stn.time_points), 2)
    
    def test_add_duplicate_time_point(self):
        """Test adding duplicate time point."""
        stn = STN()
        stn.add_time_point('A')
        stn.add_time_point('A')  # Should not create duplicate
        self.assertEqual(len(stn.time_points), 1)
    
    def test_add_constraint(self):
        """Test adding constraints to STN."""
        stn = STN()
        stn.add_constraint('A', 'B', (10, 15))
        self.assertIn('A', stn.time_points)
        self.assertIn('B', stn.time_points)
        self.assertIn(('A', 'B'), stn.constraints)
        self.assertEqual(stn.constraints[('A', 'B')], (10, 15))
    
    def test_add_constraint_invalid(self):
        """Test adding invalid constraint (min > max)."""
        stn = STN()
        with self.assertRaises(ValueError):
            stn.add_constraint('A', 'B', (20, 10))  # min > max
    
    def test_add_interval(self):
        """Test adding interval constraint."""
        stn = STN()
        stn.add_interval('start', 'end', (5, 10))
        self.assertIn(('start', 'end'), stn.constraints)
        self.assertEqual(stn.constraints[('start', 'end')], (5, 10))
    
    def test_consistent_simple(self):
        """Test consistency checking with simple consistent STN."""
        stn = STN()
        stn.add_time_point('A')
        stn.add_time_point('B')
        stn.add_constraint('A', 'B', (0, 10))
        self.assertTrue(stn.consistent())
    
    def test_consistent_inconsistent(self):
        """Test consistency checking with inconsistent STN."""
        stn = STN()
        # A -> B: 10-15
        # B -> A: 10-15 (creates cycle with total min 20, but A->A must be 0)
        stn.add_constraint('A', 'B', (10, 15))
        stn.add_constraint('B', 'A', (10, 15))
        self.assertFalse(stn.consistent())
    
    def test_consistent_empty(self):
        """Test consistency of empty STN."""
        stn = STN()
        self.assertTrue(stn.consistent())
    
    def test_consistent_single_point(self):
        """Test consistency of STN with single point."""
        stn = STN()
        stn.add_time_point('A')
        self.assertTrue(stn.consistent())
    
    def test_clear(self):
        """Test clearing STN (if method exists)."""
        stn = STN()
        stn.add_time_point('A')
        stn.add_time_point('B')
        stn.add_constraint('A', 'B', (5, 10))
        
        # Check if clear method exists
        if hasattr(stn, 'clear'):
            stn.clear()
            self.assertEqual(len(stn.time_points), 0)
            self.assertEqual(len(stn.constraints), 0)
    
    def test_multiple_constraints(self):
        """Test STN with multiple constraints."""
        stn = STN()
        stn.add_constraint('A', 'B', (0, 10))
        stn.add_constraint('B', 'C', (0, 10))
        stn.add_constraint('A', 'C', (0, 25))
        
        self.assertEqual(len(stn.time_points), 3)
        self.assertEqual(len(stn.constraints), 3)
        self.assertTrue(stn.consistent())


if __name__ == '__main__':
    unittest.main()
