#!/usr/bin/env python
"""
Tests for temporal utility functions.

Covers ISO 8601 duration parsing and time arithmetic.
"""

import unittest
import sys
import os
import importlib.util
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import directly to avoid matplotlib dependency
utils_spec = importlib.util.spec_from_file_location("temporal_utils", "ipyhop/temporal/utils.py")
utils_module = importlib.util.module_from_spec(utils_spec)
utils_spec.loader.exec_module(utils_module)

parse_iso8601_duration = utils_module.parse_iso8601_duration
format_iso8601_duration = utils_module.format_iso8601_duration
parse_iso8601_datetime = utils_module.parse_iso8601_datetime
format_iso8601_datetime = utils_module.format_iso8601_datetime
add_duration_to_datetime = utils_module.add_duration_to_datetime
calculate_end_time = utils_module.calculate_end_time
duration_to_seconds = utils_module.duration_to_seconds
now_iso8601 = utils_module.now_iso8601


class TestTemporalUtils(unittest.TestCase):
    """Test temporal utility functions."""
    
    # ==================== Duration Parsing ====================
    
    def test_parse_iso8601_duration_simple(self):
        """Test parsing simple ISO 8601 durations."""
        self.assertEqual(parse_iso8601_duration("PT10S"), 10)
        self.assertEqual(parse_iso8601_duration("PT5M"), 300)
        self.assertEqual(parse_iso8601_duration("PT1H"), 3600)
    
    def test_parse_iso8601_duration_combined(self):
        """Test parsing combined ISO 8601 durations."""
        self.assertEqual(parse_iso8601_duration("PT1H30M"), 5400)
        self.assertEqual(parse_iso8601_duration("PT1H30M45S"), 5445)
        self.assertEqual(parse_iso8601_duration("PT2H15M30S"), 8130)
    
    def test_parse_iso8601_duration_decimal(self):
        """Test parsing durations with decimal seconds."""
        self.assertEqual(parse_iso8601_duration("PT0.5S"), 0.5)
        self.assertEqual(parse_iso8601_duration("PT1.5S"), 1.5)
    
    def test_parse_iso8601_duration_invalid(self):
        """Test parsing invalid durations."""
        self.assertIsNone(parse_iso8601_duration(""))
        self.assertIsNone(parse_iso8601_duration("invalid"))
        self.assertIsNone(parse_iso8601_duration("10S"))  # Missing PT
        self.assertIsNone(parse_iso8601_duration(None))
    
    # ==================== Duration Formatting ====================
    
    def test_format_iso8601_duration_simple(self):
        """Test formatting simple durations."""
        self.assertEqual(format_iso8601_duration(10), "PT10S")
        self.assertEqual(format_iso8601_duration(300), "PT5M")
        self.assertEqual(format_iso8601_duration(3600), "PT1H")
    
    def test_format_iso8601_duration_combined(self):
        """Test formatting combined durations."""
        self.assertEqual(format_iso8601_duration(3661), "PT1H1M1S")
        self.assertEqual(format_iso8601_duration(5445), "PT1H30M45S")
    
    def test_format_iso8601_duration_zero(self):
        """Test formatting zero duration."""
        self.assertEqual(format_iso8601_duration(0), "PT0S")
    
    # ==================== Duration Conversion ====================
    
    def test_duration_to_seconds_string(self):
        """Test converting string duration to seconds."""
        self.assertEqual(duration_to_seconds("PT10S"), 10)
        self.assertEqual(duration_to_seconds("PT1H"), 3600)
    
    def test_duration_to_seconds_float(self):
        """Test converting float duration to seconds."""
        self.assertEqual(duration_to_seconds(10), 10)
        self.assertEqual(duration_to_seconds(3600), 3600)
    
    def test_duration_to_seconds_invalid(self):
        """Test converting invalid duration."""
        self.assertIsNone(duration_to_seconds("invalid"))
    
    # ==================== DateTime Parsing ====================
    
    def test_parse_iso8601_datetime(self):
        """Test parsing ISO 8601 datetime."""
        dt = parse_iso8601_datetime("2024-01-01T12:00:00")
        self.assertIsInstance(dt, datetime)
        self.assertEqual(dt.year, 2024)
        self.assertEqual(dt.month, 1)
        self.assertEqual(dt.day, 1)
        self.assertEqual(dt.hour, 12)
    
    def test_parse_iso8601_datetime_with_timezone(self):
        """Test parsing datetime with timezone."""
        dt = parse_iso8601_datetime("2024-01-01T12:00:00Z")
        self.assertIsNotNone(dt)
    
    def test_parse_iso8601_datetime_invalid(self):
        """Test parsing invalid datetime."""
        self.assertIsNone(parse_iso8601_datetime(""))
        self.assertIsNone(parse_iso8601_datetime("invalid"))
    
    # ==================== DateTime Formatting ====================
    
    def test_format_iso8601_datetime(self):
        """Test formatting datetime to ISO 8601."""
        dt = datetime(2024, 1, 1, 12, 0, 0)
        formatted = format_iso8601_datetime(dt)
        self.assertEqual(formatted, "2024-01-01T12:00:00")
    
    # ==================== Time Arithmetic ====================
    
    def test_add_duration_to_datetime(self):
        """Test adding duration to datetime."""
        result = add_duration_to_datetime("2024-01-01T00:00:00", 10)
        # Returns datetime object
        self.assertIsInstance(result, datetime)
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 1)
        self.assertEqual(result.hour, 0)
        self.assertEqual(result.minute, 0)
        self.assertEqual(result.second, 10)
    
    def test_add_duration_to_datetime_with_iso_duration(self):
        """Test adding ISO duration to datetime."""
        result = add_duration_to_datetime("2024-01-01T00:00:00", "PT10S")
        # Returns datetime object
        self.assertIsInstance(result, datetime)
        self.assertEqual(result.second, 10)
    
    def test_calculate_end_time(self):
        """Test calculating end time."""
        end_time = calculate_end_time("2024-01-01T00:00:00", 10)
        # Returns ISO 8601 string with Z suffix
        self.assertEqual(end_time, "2024-01-01T00:00:10Z")
    
    def test_calculate_end_time_with_iso_duration(self):
        """Test calculating end time with ISO duration."""
        end_time = calculate_end_time("2024-01-01T00:00:00", "PT10S")
        self.assertEqual(end_time, "2024-01-01T00:00:10Z")
    
    def test_format_iso8601_datetime(self):
        """Test formatting datetime to ISO 8601."""
        dt = datetime(2024, 1, 1, 12, 0, 0)
        formatted = format_iso8601_datetime(dt)
        # Returns string with Z suffix
        self.assertEqual(formatted, "2024-01-01T12:00:00Z")
    
    # ==================== Current Time ====================
    
    def test_now_iso8601(self):
        """Test getting current time in ISO 8601 format."""
        time_str = now_iso8601()
        self.assertIsNotNone(time_str)
        self.assertIn('T', time_str)
        # Verify it's a valid datetime
        dt = parse_iso8601_datetime(time_str)
        self.assertIsInstance(dt, datetime)


if __name__ == '__main__':
    unittest.main()
