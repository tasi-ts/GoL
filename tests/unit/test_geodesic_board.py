import copy
import random

import pytest

from gol.geodesic_board import GeodesicBoard

pytestmark = pytest.mark.unit


def test_new_board_is_empty():
    board = GeodesicBoard(2)
    assert board.cells == set()
    assert board.area == 0
    assert board.cell_count == 42
    assert board.size == 2


def test_set_alive_and_is_alive():
    board = GeodesicBoard(2)
    board.set_alive(3, True)
    assert board.is_alive(3)
    assert 3 in board.live_cells
    board.set_alive(3, False)
    assert not board.is_alive(3)


def test_add_object_sets_area():
    board = GeodesicBoard(2)
    board.add_object({0, 1, 2})
    assert board.area == 3
    assert board.live_cells == {0, 1, 2}


def test_add_random_coords_default_rate_is_half():
    random.seed(0)
    board = GeodesicBoard(2)
    board.add_random_coords()
    assert board.area == 21


def test_add_random_coords_honors_rate():
    random.seed(1)
    board = GeodesicBoard(2)
    board.add_random_coords(rate=0.25)
    assert board.area == 10


def test_neighbors_come_from_mesh():
    board = GeodesicBoard(2)
    assert board.neighbors(0) is board.mesh.adjacency[0]
    assert 0 not in board.neighbors(0)


def test_deepcopy_shares_mesh_and_copies_cells():
    board = GeodesicBoard(2)
    board.add_object({4, 5})
    clone = copy.deepcopy(board)
    assert clone.mesh is board.mesh
    clone.set_alive(4, False)
    clone.set_alive(7, True)
    assert board.is_alive(4)
    assert not board.is_alive(7)
    assert clone.live_cells == {5, 7}
