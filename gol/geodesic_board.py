from .geodesic_mesh import GeodesicMesh
from .seeding import make_rng, target_live_count


class GeodesicBoard:
    """Sphere board: live cells are integer mesh vertex ids."""

    def __init__(self, frequency):
        self.frequency = frequency
        self.mesh = GeodesicMesh(frequency)
        self.cells = set()

    @property
    def cell_count(self):
        return self.mesh.cell_count

    @property
    def size(self):
        return self.frequency

    @property
    def live_cells(self):
        return self.cells

    @property
    def area(self):
        return len(self.cells)

    def is_alive(self, cell):
        return cell in self.cells

    def set_alive(self, cell, alive):
        if alive:
            self.cells.add(cell)
        else:
            self.cells.discard(cell)

    def neighbors(self, cell):
        return self.mesh.adjacency[cell]

    def calc_area(self):
        """No-op: ``area`` is ``len(live_cells)``."""

    def add_object(self, coord_set):
        self.cells = self.cells.union(coord_set)

    def add_random_coords(self, rate=None, seed=None):
        num = target_live_count(self.cell_count, rate)
        candidates = list(range(self.cell_count))
        make_rng(seed).shuffle(candidates)
        for cell_id in candidates[:num]:
            self.cells.add(cell_id)

    def print_cells(self):
        print(self.cells, end="\n\n")

    def print_area(self):
        print("Area: {}".format(self.area), end="\n\n")

    def __deepcopy__(self, memo):
        new_board = object.__new__(GeodesicBoard)
        memo[id(self)] = new_board
        new_board.frequency = self.frequency
        new_board.mesh = self.mesh
        new_board.cells = set(self.cells)
        return new_board
