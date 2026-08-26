import pytest

from gol.topology import Topology

pytestmark = pytest.mark.unit


def test_labels():
    assert Topology.BOUNDED.label() == "Bounded"
    assert Topology.TOROIDAL.label() == "Toroidal"
    assert Topology.SPHERE.label() == "Sphere"


def test_next_and_prev_cycle():
    assert Topology.BOUNDED.next() == Topology.TOROIDAL
    assert Topology.TOROIDAL.next() == Topology.SPHERE
    assert Topology.SPHERE.next() == Topology.BOUNDED
    assert Topology.BOUNDED.prev() == Topology.SPHERE
    assert Topology.TOROIDAL.prev() == Topology.BOUNDED
    assert Topology.SPHERE.prev() == Topology.TOROIDAL


def test_from_toroidal():
    assert Topology.from_toroidal(True) == Topology.TOROIDAL
    assert Topology.from_toroidal(False) == Topology.BOUNDED
