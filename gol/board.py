import copy
from typing import Protocol, runtime_checkable

import matplotlib.pyplot as plt

from .seeding import make_rng, target_live_count


@runtime_checkable
class BoardProtocol(Protocol):
    """Shared surface used by ``GameOfLife`` for flat and geodesic boards."""

    cells: set

    @property
    def cell_count(self) -> int: ...

    @property
    def live_cells(self) -> set: ...

    @property
    def area(self) -> int: ...

    def is_alive(self, cell) -> bool: ...

    def set_alive(self, cell, alive: bool) -> None: ...

    def neighbors(self, cell): ...

    def add_object(self, coord_set) -> None: ...

    def add_random_coords(self, rate=None, seed=None) -> None: ...

    def calc_area(self) -> None: ...


class FlatBoard:
    """Square grid board. Live cells are ``(row, column)`` pairs."""

    def __init__(self, size, rules=None) -> None:
        self.size = size
        self.rules = rules
        self.cells = set()

    @property
    def cell_count(self):
        return self.size * self.size

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
        if self.rules is None:
            raise RuntimeError("FlatBoard requires Rules for neighbor lookup")
        x, y = cell
        return self.rules.neighbors(x, y)

    def print_cells(self):
        print(self.cells, end="\n\n")

    def print_area(self):
        print("Area: {}".format(self.area), end="\n\n")

    def print_board(self):
        for i in range(self.size):
            for j in range(self.size):
                print("{0}".format(1 if self.is_alive((i, j)) else 0), end=" ")
            print()
        print()

    def convert_to_binary_image(self):
        return [
            [255 if self.is_alive((j, i)) else 0 for i in range(self.size)]
            for j in range(self.size)
        ]

    def display_board(self):
        img = self.convert_to_binary_image()
        plt.imshow(img, cmap="gray")
        plt.show()

    def add_object(self, coord_set):
        self.cells = self.cells.union(coord_set)

    def add_random_coords(self, rate=None, seed=None):
        num = target_live_count(self.cell_count, rate)
        rng = make_rng(seed)
        added = 0
        while added < num:
            cell = (rng.randrange(self.size), rng.randrange(self.size))
            if cell not in self.cells:
                self.cells.add(cell)
                added += 1

    def calc_area(self):
        """No-op: ``area`` is ``len(live_cells)``."""

    def __deepcopy__(self, memo):
        new_board = object.__new__(FlatBoard)
        memo[id(self)] = new_board
        new_board.size = self.size
        new_board.rules = copy.deepcopy(self.rules, memo) if self.rules else None
        new_board.cells = set(self.cells)
        return new_board


# Backward-compatible alias.
Board = FlatBoard
