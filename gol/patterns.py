"""Named Life patterns as live-cell coordinates on a flat board.

Coordinates are ``(row, column)`` pairs for ``FlatBoard``. Sphere topologies
are unsupported: geodesic cells are mesh vertex ids, not grid coords.
"""

from .types import Coord

# Still lifes
#
#       1 2
#    1  O O
#    2  O O
BLOCK: frozenset[Coord] = frozenset({(1, 1), (1, 2), (2, 1), (2, 2)})
#
#       1 2 3 4
#    1  . O O .
#    2  O . . O
#    3  . O O .
BEEHIVE: frozenset[Coord] = frozenset({(1, 2), (1, 3), (2, 1), (2, 4), (3, 2), (3, 3)})

# Oscillators (Moore neighborhood)
#
#       3
#    2  O
#    3  O
#    4  O
BLINKER_V: frozenset[Coord] = frozenset({(2, 3), (3, 3), (4, 3)})
#
#       2 3 4
#    3  O O O
BLINKER_H: frozenset[Coord] = frozenset({(3, 2), (3, 3), (3, 4)})
#
#       1 2 3 4
#    2  . O O O
#    3  O O O .
TOAD_A: frozenset[Coord] = frozenset({(2, 2), (2, 3), (2, 4), (3, 1), (3, 2), (3, 3)})

# Spaceship (Moore neighborhood)
#
#       1 2 3
#    1  . O .
#    2  . . O
#    3  O O O
GLIDER: frozenset[Coord] = frozenset({(1, 2), (2, 3), (3, 1), (3, 2), (3, 3)})

# Stable CLI names (``gol --pattern``). Flat boards only.
CLI_PATTERNS: dict[str, frozenset[Coord]] = {
    "block": BLOCK,
    "blinker": BLINKER_V,
    "toad": TOAD_A,
    "glider": GLIDER,
    "beehive": BEEHIVE,
}


def get_pattern(name: str) -> frozenset[Coord]:
    try:
        return CLI_PATTERNS[name]
    except KeyError:
        known = ", ".join(CLI_PATTERNS)
        raise ValueError("unknown pattern {0!r}; choose from {1}".format(name, known))
