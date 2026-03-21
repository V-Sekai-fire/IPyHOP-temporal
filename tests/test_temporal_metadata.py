#!/usr/bin/env python
"""
Tests for TemporalMetadata class.

Covers temporal metadata handling for actions with duration.
"""

import unittest
import sys
import os
import importlib.util

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import directly to avoid matplotlib dependency
tm_spec = importlib.util.spec_from_file_location("temporal_metadata", "ipyhop/temporal_metadata.py")
tm_module = importlib.util.module_from_spec(tm_spec)
tm_spec.loader.exec_module(tm_module)
TemporalMetadata = tm_module.TemporalMetadata


class TestTemporalMetadata(unittest.TestCase):
    """Test TemporalMetadata class."""
    
    def test_initialization(self):
        """Test TemporalMetadata initialization."""
        tm = TemporalMetadata(duration=10)
        # Duration is stored as ISO 8601 format
        self.assertEqual(tm.duration, "PT10S")
        self.assertIsNone(tm.start_time)
        self.assertIsNone(tm.end_time)
    
    def test_initialization_with_iso_duration(self):
        """Test initialization with ISO 8601 duration."""
        tm = TemporalMetadata(duration="PT10S")
        self.assertEqual(tm.duration, "PT10S")
    
    def test_set_start_time(self):
        """Test setting start time."""
        tm = TemporalMetadata(duration=10)
        tm.set_start_time("2024-01-01T00:00:00")
        self.assertEqual(tm.start_time, "2024-01-01T00:00:00")
    
    def test_set_end_time(self):
        """Test setting end time."""
        tm = TemporalMetadata(duration=10)
        tm.set_end_time("2024-01-01T00:00:10")
        self.assertEqual(tm.end_time, "2024-01-01T00:00:10")
    
    def test_calculate_end_from_duration(self):
        """Test calculating end time from duration."""
        tm = TemporalMetadata(duration=10)
        tm.set_start_time("2024-01-01T00:00:00")
        tm.calculate_end_from_duration()
        self.assertIsNotNone(tm.end_time)
        # End time should be 10 seconds after start (with Z suffix)
        self.assertEqual(tm.end_time, "2024-01-01T00:00:10Z")
    
    def test_set_duration(self):
        """Test setting duration."""
        tm = TemporalMetadata()
        tm.set_duration(10)
        self.assertEqual(tm.duration, "PT10S")
        
        tm.set_duration("PT5M")
        self.assertEqual(tm.duration, "PT5M")
    
    def test_to_dict(self):
        """Test converting to dictionary."""
        tm = TemporalMetadata(duration=10)
        tm.set_start_time("2024-01-01T00:00:00")
        tm.set_end_time("2024-01-01T00:00:10")
        d = tm.to_dict()
        self.assertIn('duration', d)
        self.assertIn('start_time', d)
        self.assertIn('end_time', d)
        self.assertEqual(d['duration'], "PT10S")
    
    def test_from_dict(self):
        """Test creating from dictionary."""
        d = {
            'duration': "PT10S",
            'start_time': "2024-01-01T00:00:00",
            'end_time': "2024-01-01T00:00:10"
        }
        tm = TemporalMetadata.from_dict(d)
        self.assertEqual(tm.duration, "PT10S")
        self.assertEqual(tm.start_time, "2024-01-01T00:00:00")
        self.assertEqual(tm.end_time, "2024-01-01T00:00:10")
    
    def test_copy(self):
        """Test copying TemporalMetadata."""
        tm = TemporalMetadata(duration=10)
        tm.set_start_time("2024-01-01T00:00:00")
        tm_copy = tm.copy()
        self.assertEqual(tm_copy.duration, tm.duration)
        self.assertEqual(tm_copy.start_time, tm.start_time)
        # Modify copy's duration
        tm_copy.set_duration(20)
        self.assertEqual(tm.duration, "PT10S")
        self.assertEqual(tm_copy.duration, "PT20S")
    
    def test_string_representation(self):
        """Test string representation."""
        tm = TemporalMetadata(duration=10)
        tm.set_start_time("2024-01-01T00:00:00")
        tm.set_end_time("2024-01-01T00:00:10")
        str_repr = str(tm)
        self.assertIn('duration', str_repr)
        self.assertIn('10', str_repr)


if __name__ == '__main__':
    unittest.main()
