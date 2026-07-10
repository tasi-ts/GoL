import copy
import random

from geodesic_mesh import GeodesicMesh


class GeodesicBoard:
    """Sphere board: live cells are integer mesh vertex ids."""

    def __init__(self, frequency):
        self.frequency = frequency
        self.mesh = GeodesicMesh(frequency)
        self.cells = set()
        self.area = 0

    @property
    def cell_count(self):
        return self.mesh.cell_count

    @property
    def size(self):
        return self.frequency

    @property
    def live_cells(self):
        return self.cells

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
        self.area = len(self.cells)

    def add_object(self, coord_set):
        self.cells = self.cells.union(coord_set)
        self.calc_area()

    def add_random_coords(self, rate=None):
        if rate is None:
            num = int(self.cell_count * 0.5)
        else:
            num = int(self.cell_count * rate)
        candidates = list(range(self.cell_count))
        random.shuffle(candidates)
        for cell_id in candidates[:num]:
            self.cells.add(cell_id)
        self.calc_area()

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
        new_board.area = self.area
        return new_board
