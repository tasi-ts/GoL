import copy

import pytest

from gol.board import Board, BoardProtocol, FlatBoard
from gol.geodesic_board import GeodesicBoard
from gol.rules import Rules

pytestmark = pytest.mark.unit


def _board(size=5, neighborhood=8, toroidal=False):
    return FlatBoard(size, rules=Rules(neighborhood, size, toroidal=toroidal))


def test_board_alias_is_flat_board():
    assert Board is FlatBoard


def test_flat_and_geodesic_satisfy_protocol():
    assert isinstance(_board(), BoardProtocol)
    assert isinstance(GeodesicBoard(2), BoardProtocol)


def test_new_board_is_empty():
    board = _board()
    assert board.cells == set()
    assert board.area == 0
    assert board.cell_count == 25
    assert not any(board.is_alive((i, j)) for i in range(5) for j in range(5))


def test_set_alive_updates_live_cells():
    board = _board()
    board.set_alive((1, 2), True)
    assert board.is_alive((1, 2))
    assert (1, 2) in board.cells
    board.set_alive((1, 2), False)
    assert not board.is_alive((1, 2))
    assert (1, 2) not in board.cells


def test_area_tracks_live_cells():
    board = _board()
    board.set_alive((0, 0), True)
    assert board.area == 1
    board.set_alive((0, 0), False)
    assert board.area == 0


def test_add_object_sets_area():
    board = _board()
    board.add_object({(0, 0), (1, 1)})
    assert board.area == 2
    assert board.live_cells == {(0, 0), (1, 1)}


def test_add_random_coords_default_rate_is_half():
    board = _board(size=10)
    board.add_random_coords(seed=0)
    assert board.area == 50
    assert len(board.cells) == 50


def test_add_random_coords_honors_rate():
    board = _board(size=10)
    board.add_random_coords(rate=0.2, seed=1)
    assert board.area == 20


def test_same_seed_reproduces_live_cells():
    first = _board(size=10)
    second = _board(size=10)
    first.add_random_coords(rate=0.3, seed=42)
    second.add_random_coords(rate=0.3, seed=42)
    assert first.live_cells == second.live_cells


def test_neighbors_require_rules():
    board = FlatBoard(4)
    with pytest.raises(RuntimeError, match="requires Rules"):
        board.neighbors((1, 1))


def test_neighbors_delegate_to_rules():
    board = _board(size=5, neighborhood=4)
    neighbors = board.neighbors((0, 0))
    assert neighbors == {(0, 1), (1, 0)}


def test_deepcopy_is_independent():
    board = _board()
    board.add_object({(2, 2)})
    clone = copy.deepcopy(board)
    clone.set_alive((2, 2), False)
    clone.set_alive((0, 0), True)
    assert board.is_alive((2, 2))
    assert not board.is_alive((0, 0))
    assert clone.area == 1
    assert board.area == 1
    assert not hasattr(board, "array")
    assert not hasattr(clone, "array")
