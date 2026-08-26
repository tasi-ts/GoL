import pytest

from gol.seeding import DEFAULT_FILL_RATE, target_live_count

pytestmark = pytest.mark.unit


def test_default_rate_is_half():
    assert DEFAULT_FILL_RATE == 0.5
    assert target_live_count(100) == 50
    assert target_live_count(100, None) == 50


def test_explicit_rate():
    assert target_live_count(10, 0.2) == 2
    assert target_live_count(16, 0.4) == 6
