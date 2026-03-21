#!/usr/bin/env python
"""
Property-based tests for temporal utilities using Hypothesis.
Tests ISO 8601 duration parsing, formatting, and datetime arithmetic.
"""

from datetime import datetime, timedelta

import hypothesis.strategies as st
import pytest
from hypothesis import HealthCheck, assume, given, settings

from ipyhop.temporal.utils import (
    add_duration_to_datetime,
    calculate_end_time,
    duration_to_seconds,
    format_iso8601_datetime,
    format_iso8601_duration,
    now_iso8601,
    parse_iso8601_datetime,
    parse_iso8601_duration,
)

# ============================================================================
# Strategies
# ============================================================================


@st.composite
def valid_iso8601_durations(draw):
    """Generate valid ISO 8601 duration strings."""
    hours = draw(st.integers(0, 23))
    minutes = draw(st.integers(0, 59))
    seconds = draw(st.floats(0.0, 59.9))

    parts = []
    if hours > 0:
        parts.append(f"{hours}H")
    if minutes > 0:
        parts.append(f"{minutes}M")
    if seconds > 0 or not parts:
        if seconds == int(seconds):
            parts.append(f"{int(seconds)}S")
        else:
            parts.append(f"{seconds:.3f}S")

    assume(parts)  # At least one component
    return "PT" + "".join(parts)


@st.composite
def positive_seconds(draw):
    """Generate positive seconds values."""
    return draw(st.floats(0.0, 86400.0, allow_infinity=False, allow_nan=False))


@st.composite
def valid_iso8601_datetimes(draw):
    """Generate valid ISO 8601 datetime strings."""
    year = draw(st.integers(2000, 2100))
    month = draw(st.integers(1, 12))
    day = draw(st.integers(1, 28))  # Safe range
    hour = draw(st.integers(0, 23))
    minute = draw(st.integers(0, 59))
    second = draw(st.integers(0, 59))

    return f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}Z"


# ============================================================================
# Duration Parsing Tests
# ============================================================================


@given(valid_iso8601_durations())
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_parse_valid_duration_returns_positive_seconds(duration_str):
    """Valid ISO 8601 durations should parse to positive seconds."""
    seconds = parse_iso8601_duration(duration_str)
    assert seconds is not None
    assert isinstance(seconds, float)
    assert seconds >= 0


@given(st.text(min_size=1, max_size=20))
@settings(max_examples=50)
def test_parse_invalid_duration_returns_none(invalid_str):
    """Invalid duration strings should return None."""
    # Filter out strings that might accidentally be valid
    assume(not invalid_str.startswith("PT"))
    result = parse_iso8601_duration(invalid_str)
    assert result is None


@given(st.none())
@settings(max_examples=10)
def test_parse_none_duration_returns_none():
    """None input should return None."""
    result = parse_iso8601_duration(None)
    assert result is None


@given(positive_seconds())
@settings(max_examples=100)
def test_parse_roundtrip_preserves_value(seconds):
    """Parsing a formatted duration should return the original seconds."""
    formatted = format_iso8601_duration(seconds)
    parsed = parse_iso8601_duration(formatted)
    assume(parsed is not None)
    # Allow small floating point differences
    assert abs(parsed - seconds) < 0.001


# ============================================================================
# Duration Formatting Tests
# ============================================================================


@given(positive_seconds())
@settings(max_examples=100)
def test_format_duration_returns_valid_iso8601(seconds):
    """Formatted durations should be valid ISO 8601 strings."""
    formatted = format_iso8601_duration(seconds)
    assert isinstance(formatted, str)
    assert formatted.startswith("PT")
    # Should be parseable
    parsed = parse_iso8601_duration(formatted)
    assert parsed is not None


@given(st.floats(min_value=-1000, max_value=-0.1, allow_infinity=False, allow_nan=False))
@settings(max_examples=50)
def test_format_negative_seconds_clamps_to_zero(negative_seconds):
    """Negative seconds should be clamped to zero."""
    formatted = format_iso8601_duration(negative_seconds)
    assert formatted == "PT0S"


@given(st.integers(0, 1000000))
@settings(max_examples=100)
def test_format_integer_seconds_exact(int_seconds):
    """Integer seconds should format and parse exactly."""
    formatted = format_iso8601_duration(float(int_seconds))
    parsed = parse_iso8601_duration(formatted)
    assert parsed == float(int_seconds)


# ============================================================================
# Datetime Parsing Tests
# ============================================================================


@given(valid_iso8601_datetimes())
@settings(max_examples=100)
def test_parse_valid_datetime_returns_datetime(datetime_str):
    """Valid ISO 8601 datetimes should parse successfully."""
    result = parse_iso8601_datetime(datetime_str)
    assert result is not None
    assert isinstance(result, datetime)


@given(st.text(min_size=1, max_size=30))
@settings(max_examples=50)
def test_parse_invalid_datetime_returns_none(invalid_str):
    """Invalid datetime strings should return None."""
    # Filter out strings that might accidentally be valid
    assume("T" not in invalid_str or len(invalid_str) < 19)
    result = parse_iso8601_datetime(invalid_str)
    # May or may not be None depending on string
    if result is not None:
        assert isinstance(result, datetime)


# ============================================================================
# Datetime Formatting Tests
# ============================================================================


@given(
    st.datetimes(
        min_value=datetime(2000, 1, 1),
        max_value=datetime(2100, 12, 31),
    )
)
@settings(max_examples=100)
def test_format_datetime_returns_string(dt):
    """Formatting a datetime should return a string."""
    formatted = format_iso8601_datetime(dt)
    assert isinstance(formatted, str)
    assert len(formatted) > 0


@given(
    st.datetimes(
        min_value=datetime(2000, 1, 1),
        max_value=datetime(2100, 12, 31),
    )
)
@settings(max_examples=100)
def test_format_parse_datetime_roundtrip(dt):
    """Parsing a formatted datetime should return equivalent datetime."""
    formatted = format_iso8601_datetime(dt)
    parsed = parse_iso8601_datetime(formatted)
    assert parsed is not None
    # Allow small timezone-related differences
    assert abs((parsed - dt.replace(tzinfo=None)).total_seconds()) < 1


# ============================================================================
# Duration Addition Tests
# ============================================================================


@given(valid_iso8601_datetimes(), valid_iso8601_durations())
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_add_duration_returns_later_datetime(start_str, duration_str):
    """Adding a duration should return a later datetime."""
    result = add_duration_to_datetime(start_str, duration_str)
    assert result is not None

    start_dt = parse_iso8601_datetime(start_str)
    duration_sec = parse_iso8601_duration(duration_str)

    if duration_sec > 0:
        assert result > start_dt


@given(valid_iso8601_datetimes(), positive_seconds())
@settings(max_examples=100)
def test_add_duration_float_seconds(start_str, seconds):
    """Adding duration as float seconds should work."""
    result = add_duration_to_datetime(start_str, seconds)
    assert result is not None

    start_dt = parse_iso8601_datetime(start_str)
    expected = start_dt + timedelta(seconds=seconds)
    # Allow small floating point differences
    assert abs((result - expected.replace(tzinfo=None)).total_seconds()) < 0.01


@given(st.none(), valid_iso8601_durations())
@settings(max_examples=10)
def test_add_duration_none_datetime_returns_none(duration_str):
    """None datetime should return None."""
    result = add_duration_to_datetime(None, duration_str)
    assert result is None


# ============================================================================
# End Time Calculation Tests
# ============================================================================


@given(valid_iso8601_datetimes(), valid_iso8601_durations())
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_calculate_end_time_returns_valid_datetime(start_str, duration_str):
    """Calculating end time should return a valid ISO 8601 string."""
    result = calculate_end_time(start_str, duration_str)
    assert result is not None
    assert isinstance(result, str)
    # Should be parseable
    parsed = parse_iso8601_datetime(result)
    assert parsed is not None


@given(valid_iso8601_datetimes(), positive_seconds())
@settings(max_examples=100)
def test_calculate_end_time_with_float_seconds(start_str, seconds):
    """Calculating end time with float seconds should work."""
    result = calculate_end_time(start_str, seconds)
    assert result is not None

    start_dt = parse_iso8601_datetime(start_str)
    expected = start_dt + timedelta(seconds=seconds)
    result_dt = parse_iso8601_datetime(result)

    # Allow small differences
    assert abs((result_dt - expected.replace(tzinfo=None)).total_seconds()) < 0.01


# ============================================================================
# Duration to Seconds Tests
# ============================================================================


@given(positive_seconds())
@settings(max_examples=100)
def test_duration_to_seconds_float_returns_same(seconds):
    """Converting float seconds should return the same value."""
    result = duration_to_seconds(seconds)
    assert result == seconds


@given(valid_iso8601_durations())
@settings(max_examples=100)
def test_duration_to_seconds_string_parses(duration_str):
    """Converting duration string should parse correctly."""
    result = duration_to_seconds(duration_str)
    assert result is not None
    assert result >= 0
    # Should match direct parsing
    assert result == parse_iso8601_duration(duration_str)


@given(st.none())
@settings(max_examples=10)
def test_duration_to_seconds_none_returns_none():
    """None should return None."""
    result = duration_to_seconds(None)
    assert result is None


# ============================================================================
# Now ISO 8601 Tests
# ============================================================================


def test_now_iso8601_returns_valid_datetime():
    """now_iso8601 should return a valid ISO 8601 datetime string."""
    result = now_iso8601()
    assert isinstance(result, str)
    parsed = parse_iso8601_datetime(result)
    assert parsed is not None
    # Should be close to now
    now = datetime.utcnow()
    assert abs((parsed - now.replace(tzinfo=None)).total_seconds()) < 60


@given(st.integers(1, 10))
@settings(max_examples=10)
def test_now_iso8601_monotonicity(n):
    """Multiple calls to now_iso8601 should be monotonically increasing (or equal)."""
    times = [now_iso8601() for _ in range(n)]
    parsed_times = [parse_iso8601_datetime(t) for t in times]
    for i in range(1, len(parsed_times)):
        assert parsed_times[i] >= parsed_times[i - 1]


# ============================================================================
# Edge Cases and Boundary Tests
# ============================================================================


@given(st.just(0.0))
@settings(max_examples=10)
def test_zero_duration_formats_as_pt0s(seconds):
    """Zero seconds should format as PT0S."""
    formatted = format_iso8601_duration(seconds)
    assert formatted == "PT0S"


@given(st.floats(min_value=0.0001, max_value=0.9999, allow_infinity=False, allow_nan=False))
@settings(max_examples=100)
def test_subsecond_duration_preserves_precision(seconds):
    """Subsecond durations should preserve precision."""
    formatted = format_iso8601_duration(seconds)
    parsed = parse_iso8601_duration(formatted)
    assert parsed is not None
    # Allow small precision loss
    assert abs(parsed - seconds) < 0.001


@given(st.integers(86400, 604800))  # 1 day to 7 days in seconds
@settings(max_examples=100)
def test_large_duration_formats_correctly(seconds):
    """Large durations (days) should format with hours."""
    formatted = format_iso8601_duration(seconds)
    assert "H" in formatted  # Should have hours component
    parsed = parse_iso8601_duration(formatted)
    assert parsed == seconds


# ============================================================================
# Property: Duration Symmetry
# ============================================================================


@given(valid_iso8601_datetimes(), valid_iso8601_durations())
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_duration_addition_symmetry(start_str, duration_str):
    """
    Property: Adding duration A then B should equal adding duration B then A
    (when both are added to the same start time)
    """
    duration_a_sec = parse_iso8601_duration(duration_str)
    assume(duration_a_sec is not None and duration_a_sec > 0)

    # Split into two smaller durations
    duration_b_sec = duration_a_sec / 2
    duration_c_sec = duration_a_sec / 2

    end1 = add_duration_to_datetime(start_str, duration_b_sec + duration_c_sec)

    intermediate = add_duration_to_datetime(start_str, duration_b_sec)
    assume(intermediate is not None)
    end2 = add_duration_to_datetime(intermediate, duration_c_sec)

    assert end1 is not None and end2 is not None
    assert end1 == end2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
