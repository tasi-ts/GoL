import copy
from collections.abc import Iterable
from typing import Protocol, runtime_checkable

import matplotlib.pyplot as plt

from .rules import Rules
from .seeding import make_rng, target_live_count
from .types import CellT, Coord


@runtime_checkable
class BoardProtocol(Protocol[CellT]):
    """Shared surface used by ``GameOfLife`` for flat and geodesic boards."""

    cells: set[CellT]

    @property
    def cell_count(self) -> int: ...

    @property
    def live_cells(self) -> set[CellT]: ...

    @property
    def area(self) -> int: ...

    def is_alive(self, cell: CellT) -> bool: ...

    def set_alive(self, cell: CellT, alive: bool) -> None: ...

    def neighbors(self, cell: CellT) -> set[CellT]: ...

    def add_object(self, coord_set: Iterable[CellT]) -> None: ...

    def add_random_coords(
        self, rate: float | None = None, seed: int | None = None
    ) -> None: ...

    def calc_area(self) -> None: ...

    def print_area(self) -> None: ...


class FlatBoard:
    """Square grid board. Live cells are ``(row, column)`` pairs."""

    def __init__(self, size: int, rules: Rules | None = None) -> None:
        self.size = size
        self.rules = rules
        self.cells: set[Coord] = set()

    @property
    def cell_count(self) -> int:
        return self.size * self.size

    @property
    def live_cells(self) -> set[Coord]:
        return self.cells

    @property
    def area(self) -> int:
        return len(self.cells)

    def is_alive(self, cell: Coord) -> bool:
        return cell in self.cells

    def set_alive(self, cell: Coord, alive: bool) -> None:
        if alive:
            self.cells.add(cell)
        else:
            self.cells.discard(cell)

    def neighbors(self, cell: Coord) -> set[Coord]:
        if self.rules is None:
            raise RuntimeError("FlatBoard requires Rules for neighbor lookup")
        x, y = cell
        return self.rules.neighbors(x, y)

    def print_cells(self) -> None:
        print(self.cells, end="\n\n")

    def print_area(self) -> None:
        print("Area: {}".format(self.area), end="\n\n")

    def print_board(self) -> None:
        for i in range(self.size):
            for j in range(self.size):
                print("{0}".format(1 if self.is_alive((i, j)) else 0), end=" ")
            print()
        print()

    def convert_to_binary_image(self) -> list[list[int]]:
        return [
            [255 if self.is_alive((j, i)) else 0 for i in range(self.size)]
            for j in range(self.size)
        ]

    def display_board(self) -> None:
        img = self.convert_to_binary_image()
        plt.imshow(img, cmap="gray")
        plt.show()

    def add_object(self, coord_set: Iterable[Coord]) -> None:
        self.cells = self.cells.union(coord_set)

    def add_random_coords(
        self, rate: float | None = None, seed: int | None = None
    ) -> None:
        num = target_live_count(self.cell_count, rate)
        rng = make_rng(seed)
        added = 0
        while added < num:
            cell = (rng.randrange(self.size), rng.randrange(self.size))
            if cell not in self.cells:
                self.cells.add(cell)
                added += 1

    def calc_area(self) -> None:
        """No-op: ``area`` is ``len(live_cells)``."""

    def __deepcopy__(self, memo: dict[int, object]) -> "FlatBoard":
        new_board = object.__new__(FlatBoard)
        memo[id(self)] = new_board
        new_board.size = self.size
        new_board.rules = copy.deepcopy(self.rules, memo) if self.rules else None
        new_board.cells = set(self.cells)
        return new_board


# Backward-compatible alias.
Board = FlatBoard
