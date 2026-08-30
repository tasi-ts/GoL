"""Shared random-fill helpers for flat and geodesic boards."""

import random

DEFAULT_FILL_RATE = 0.5


def target_live_count(cell_count: int, rate: float | None = None) -> int:
    if rate is None:
        rate = DEFAULT_FILL_RATE
    return int(cell_count * rate)


def make_rng(seed: int | None = None) -> random.Random:
    return random.Random(seed)
