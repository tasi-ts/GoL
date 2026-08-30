from collections.abc import Iterable

from .geodesic_mesh import GeodesicMesh
from .seeding import make_rng, target_live_count
from .types import MeshId


class GeodesicBoard:
    """Sphere board: live cells are integer mesh vertex ids."""

    def __init__(self, frequency: int) -> None:
        self.frequency = frequency
        self.mesh = GeodesicMesh(frequency)
        self.cells: set[MeshId] = set()

    @property
    def cell_count(self) -> int:
        return self.mesh.cell_count

    @property
    def size(self) -> int:
        return self.frequency

    @property
    def live_cells(self) -> set[MeshId]:
        return self.cells

    @property
    def area(self) -> int:
        return len(self.cells)

    def is_alive(self, cell: MeshId) -> bool:
        return cell in self.cells

    def set_alive(self, cell: MeshId, alive: bool) -> None:
        if alive:
            self.cells.add(cell)
        else:
            self.cells.discard(cell)

    def neighbors(self, cell: MeshId) -> set[MeshId]:
        return self.mesh.adjacency[cell]

    def calc_area(self) -> None:
        """No-op: ``area`` is ``len(live_cells)``."""

    def add_object(self, coord_set: Iterable[MeshId]) -> None:
        self.cells = self.cells.union(coord_set)

    def add_random_coords(
        self, rate: float | None = None, seed: int | None = None
    ) -> None:
        num = target_live_count(self.cell_count, rate)
        candidates = list(range(self.cell_count))
        make_rng(seed).shuffle(candidates)
        for cell_id in candidates[:num]:
            self.cells.add(cell_id)

    def print_cells(self) -> None:
        print(self.cells, end="\n\n")

    def print_area(self) -> None:
        print("Area: {}".format(self.area), end="\n\n")

    def __deepcopy__(self, memo: dict[int, object]) -> "GeodesicBoard":
        new_board = object.__new__(GeodesicBoard)
        memo[id(self)] = new_board
        new_board.frequency = self.frequency
        new_board.mesh = self.mesh
        new_board.cells = set(self.cells)
        return new_board
