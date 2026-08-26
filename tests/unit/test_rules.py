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
    rules.calc_neighbors(0, 0)
    assert rules.neighbors == {(0, 1), (1, 0), (1, 1)}


def test_bounded_edge_has_five_neighbors_moore():
    rules = Rules(8, 5, toroidal=False)
    rules.calc_neighbors(0, 2)
    assert rules.neighbors == {(0, 1), (0, 3), (1, 1), (1, 2), (1, 3)}


def test_bounded_interior_has_four_neighbors_von_neumann():
    rules = Rules(4, 5, toroidal=False)
    rules.calc_neighbors(2, 2)
    assert rules.neighbors == {(1, 2), (3, 2), (2, 1), (2, 3)}
    assert rules.neighbors == set(
        (2 + dx, 2 + dy) for dx, dy in CORE_OFFSETS
    )


def test_bounded_interior_has_eight_neighbors_moore():
    rules = Rules(8, 5, toroidal=False)
    rules.calc_neighbors(2, 2)
    expected = set((2 + dx, 2 + dy) for dx, dy in CORE_OFFSETS + DIAG_OFFSETS)
    assert rules.neighbors == expected


def test_toroidal_corner_wraps_moore():
    rules = Rules(8, 5, toroidal=True)
    rules.calc_neighbors(0, 0)
    assert rules.neighbors == {
        (0, 1),
        (1, 0),
        (1, 1),
        (0, 4),
        (1, 4),
        (4, 0),
        (4, 1),
        (4, 4),
    }
    assert len(rules.neighbors) == 8


def test_toroidal_every_cell_has_full_neighborhood():
    size = 6
    for neighborhood in (4, 8):
        rules = Rules(neighborhood, size, toroidal=True)
        for x in range(size):
            for y in range(size):
                rules.calc_neighbors(x, y)
                assert len(rules.neighbors) == neighborhood
                assert (x, y) not in rules.neighbors


def test_out_of_bounds_coordinate_clears_neighbors():
    rules = Rules(8, 5, toroidal=False)
    rules.calc_neighbors(2, 2)
    assert rules.neighbors
    rules.calc_neighbors(-1, 0)
    assert rules.neighbors == set()
    rules.calc_neighbors(5, 0)
    assert rules.neighbors == set()


def test_calc_neighbors_replaces_previous_result():
    rules = Rules(4, 5, toroidal=False)
    rules.calc_neighbors(0, 0)
    first = set(rules.neighbors)
    rules.calc_neighbors(2, 2)
    assert rules.neighbors != first
    assert (1, 2) in rules.neighbors
