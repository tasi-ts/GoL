import pytest

from gol.geodesic_mesh import GeodesicMesh

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "frequency, expected",
    [(1, 12), (2, 42), (4, 162), (8, 642)],
)
def test_cell_count_matches_formula(frequency, expected):
    mesh = GeodesicMesh(frequency)
    assert GeodesicMesh.expected_cell_count(frequency) == expected
    assert mesh.cell_count == expected
    assert len(mesh.vertices) == expected
    assert len(mesh.adjacency) == expected
    assert len(mesh.cell_polygons) == expected


def test_frequency_must_be_at_least_one():
    with pytest.raises(ValueError, match="frequency must be >= 1"):
        GeodesicMesh(0)


def test_icosahedron_all_cells_degree_five():
    mesh = GeodesicMesh(1)
    degrees = [len(neighbors) for neighbors in mesh.adjacency]
    assert degrees == [5] * 12


def test_higher_frequency_has_twelve_pentagons_rest_hexagons():
    mesh = GeodesicMesh(4)
    degrees = [len(neighbors) for neighbors in mesh.adjacency]
    assert degrees.count(5) == 12
    assert degrees.count(6) == mesh.cell_count - 12
    assert set(degrees) == {5, 6}


def test_adjacency_is_symmetric_and_excludes_self():
    mesh = GeodesicMesh(3)
    for cell, neighbors in enumerate(mesh.adjacency):
        assert cell not in neighbors
        for other in neighbors:
            assert cell in mesh.adjacency[other]


def test_vertices_lie_on_unit_sphere():
    mesh = GeodesicMesh(2)
    norms = (mesh.vertices ** 2).sum(axis=1) ** 0.5
    assert all(abs(norm - 1.0) < 1e-9 for norm in norms)


def test_cell_polygons_match_degree():
    mesh = GeodesicMesh(2)
    for cell_id, neighbors in enumerate(mesh.adjacency):
        assert len(mesh.cell_polygons[cell_id]) == len(neighbors)
