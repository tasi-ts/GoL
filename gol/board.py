import copy
import random

import matplotlib.pyplot as plt


class FlatBoard:
    """Square grid board implementing the shared board protocol."""

    def __init__(self, size, rules=None) -> None:
        self.size = size
        self.rules = rules
        self.array = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.cells = set()
        self.area = 0

    @property
    def cell_count(self):
        return self.size * self.size

    @property
    def live_cells(self):
        return self.cells

    def is_alive(self, cell):
        x, y = cell
        return self.array[x][y] == 1

    def set_alive(self, cell, alive):
        x, y = cell
        self.array[x][y] = 1 if alive else 0
        if alive:
            self.cells.add(cell)
        else:
            self.cells.discard(cell)

    def neighbors(self, cell):
        if self.rules is None:
            raise RuntimeError("FlatBoard requires Rules for neighbor lookup")
        x, y = cell
        self.rules.calc_neighbors(x, y)
        return self.rules.neighbors

    def print_cells(self):
        print(self.cells, end="\n\n")

    def print_area(self):
        print("Area: {}".format(self.area), end="\n\n")

    def print_board(self):
        for i in range(self.size):
            for j in range(self.size):
                print("{0}".format(self.array[i][j]), end=" ")
            print()
        print()

    def convert_to_binary_image(self):
        return [
            [self.array[j][i] * 255 for i in range(self.size)]
            for j in range(self.size)
        ]

    def display_board(self):
        img = self.convert_to_binary_image()
        plt.imshow(img, cmap="gray")
        plt.show()

    def add_object(self, coord_set):
        self.cells = self.cells.union(coord_set)
        for elem in coord_set:
            x, y = elem
            self.array[x][y] = 1
        self.calc_area()

    def add_random_coords(self, rate=None):
        if rate is None:
            num = int(self.size * self.size * 0.5)
        else:
            num = int(self.size * self.size * rate)
        cnt = 0
        while cnt < num:
            x = random.randrange(self.size)
            y = random.randrange(self.size)
            if (x, y) not in self.cells:
                self.cells.add((x, y))
                self.array[x][y] = 1
                cnt += 1
        self.calc_area()

    def calc_area(self):
        area_array = int(sum([sum(row) for row in self.array]))
        area_cells = len(self.cells)
        if not area_array == area_cells:
            raise Exception("--- Area is inconsistent! ---")
        self.area = area_cells

    def __deepcopy__(self, memo):
        new_board = object.__new__(FlatBoard)
        memo[id(self)] = new_board
        new_board.size = self.size
        new_board.rules = copy.deepcopy(self.rules, memo) if self.rules else None
        new_board.array = copy.deepcopy(self.array, memo)
        new_board.cells = set(self.cells)
        new_board.area = self.area
        return new_board


# Backward-compatible alias.
Board = FlatBoard
