"""Canonical Life patterns and board/game builders for characterization tests.

Coordinates are (row, column) pairs in ``FlatBoard.live_cells``.
"""

from gol.board import FlatBoard
from gol.game import GameOfLife
from gol.geodesic_board import GeodesicBoard
from gol.rules import Rules

# Still lifes
BLOCK = frozenset({(1, 1), (1, 2), (2, 1), (2, 2)})
BEEHIVE = frozenset({(1, 2), (1, 3), (2, 1), (2, 4), (3, 2), (3, 3)})

# Oscillators (Moore neighborhood)
BLINKER_V = frozenset({(2, 3), (3, 3), (4, 3)})
BLINKER_H = frozenset({(3, 2), (3, 3), (3, 4)})
TOAD_A = frozenset({(2, 2), (2, 3), (2, 4), (3, 1), (3, 2), (3, 3)})

# Spaceship (Moore neighborhood)
GLIDER = frozenset({(1, 2), (2, 3), (3, 1), (3, 2), (3, 3)})


def seed_flat_game(
    cells,
    size=8,
    neighborhood=8,
    toroidal=False,
    max_iter=50,
    rand_rate=0,
):
    rules = Rules(neighborhood, size, toroidal=toroidal)
    board = FlatBoard(size, rules=rules)
    if cells:
        board.add_object(set(cells))
    game = GameOfLife(
        board, rule_set=rules, max_iter=max_iter, rand_rate=rand_rate
    )
    game.initialize_board()
    return game


def seed_sphere_game(cells=(), frequency=2, max_iter=20, rand_rate=0):
    board = GeodesicBoard(frequency)
    if cells:
        board.add_object(set(cells))
    game = GameOfLife(
        board, rule_set=None, max_iter=max_iter, rand_rate=rand_rate
    )
    game.initialize_board()
    return game
