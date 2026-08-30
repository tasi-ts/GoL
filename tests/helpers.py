"""Canonical Life patterns and board/game builders for characterization tests.

Pattern coordinates live in ``gol.patterns`` (single source of truth).
"""

from gol.board import FlatBoard
from gol.game import GameOfLife
from gol.geodesic_board import GeodesicBoard
from gol.patterns import (
    BEEHIVE,
    BLINKER_H,
    BLINKER_V,
    BLOCK,
    GLIDER,
    TOAD_A,
)
from gol.rules import Rules

__all__ = [
    "BEEHIVE",
    "BLINKER_H",
    "BLINKER_V",
    "BLOCK",
    "GLIDER",
    "TOAD_A",
    "seed_flat_game",
    "seed_sphere_game",
]


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
