import pytest

from gol.rules import CORE_OFFSETS, DIAG_OFFSETS, Rules

pytestmark = pytest.mark.unit


def test_neighborhood_must_be_4_or_8():
    with pytest.raises(ValueError, match="Neighborhood must be 4 or 8"):
        Rules(6, 8)


def test_size_must_be_greater_than_2():
    with pytest.raises(ValueError, match="Size must be greater than 2"):
        Rules(8, 2)


def test_toroidal_must_be_bool():
    with pytest.raises(ValueError, match="Toroidal must be True or False"):
        Rules(8, 8, toroidal="yes")


def test_bounded_corner_has_three_neighbors_moore():
    rules = Rules(8, 5, toroidal=False)
    assert rules.neighbors(0, 0) == {(0, 1), (1, 0), (1, 1)}


def test_bounded_edge_has_five_neighbors_moore():
    rules = Rules(8, 5, toroidal=False)
    assert rules.neighbors(0, 2) == {(0, 1), (0, 3), (1, 1), (1, 2), (1, 3)}


def test_bounded_interior_has_four_neighbors_von_neumann():
    rules = Rules(4, 5, toroidal=False)
    expected = {(2 + dx, 2 + dy) for dx, dy in CORE_OFFSETS}
    assert rules.neighbors(2, 2) == expected


def test_bounded_interior_has_eight_neighbors_moore():
    rules = Rules(8, 5, toroidal=False)
    expected = {(2 + dx, 2 + dy) for dx, dy in CORE_OFFSETS + DIAG_OFFSETS}
    assert rules.neighbors(2, 2) == expected


def test_toroidal_corner_wraps_moore():
    rules = Rules(8, 5, toroidal=True)
    assert rules.neighbors(0, 0) == {
        (0, 1),
        (1, 0),
        (1, 1),
        (0, 4),
        (1, 4),
        (4, 0),
        (4, 1),
        (4, 4),
    }
    assert len(rules.neighbors(0, 0)) == 8


def test_toroidal_every_cell_has_full_neighborhood():
    size = 6
    for neighborhood in (4, 8):
        rules = Rules(neighborhood, size, toroidal=True)
        for x in range(size):
            for y in range(size):
                neighbors = rules.neighbors(x, y)
                assert len(neighbors) == neighborhood
                assert (x, y) not in neighbors


def test_out_of_bounds_coordinate_returns_empty():
    rules = Rules(8, 5, toroidal=False)
    assert rules.neighbors(2, 2)
    assert rules.neighbors(-1, 0) == set()
    assert rules.neighbors(5, 0) == set()


def test_neighbors_does_not_mutate_a_shared_cache():
    rules = Rules(4, 5, toroidal=False)
    first = rules.neighbors(0, 0)
    second = rules.neighbors(2, 2)
    assert first != second
    assert (0, 1) in first
    assert (1, 2) in second
    assert first is not second
