import copy

from board import Board, FlatBoard
from geodesic_board import GeodesicBoard
from rules import Rules

MAX_DETECTED_PERIOD = 6


class GameOfLife:

    def __init__(self, init_board, rule_set=None, max_iter=2500, rand_rate=0.5) -> None:
        self.board = init_board
        if isinstance(init_board, FlatBoard) and rule_set is not None:
            init_board.rules = rule_set
        self.rule_set = rule_set
        self.max_iter = max_iter
        self.rand_rate = rand_rate
        self.sequence = []
        self._initial_board = None

    def check_area(self, board, cell):
        summa = 0
        dead_cells = set()
        for neighbor in board.neighbors(cell):
            if board.is_alive(neighbor):
                summa += 1
            else:
                dead_cells.add(neighbor)
        return summa, dead_cells

    def advance_board(self):
        old_board = copy.deepcopy(self.board)
        for cell in old_board.live_cells:
            summa, dead_cells = self.check_area(old_board, cell)
            if summa < 2 and old_board.is_alive(cell):
                self.board.set_alive(cell, False)
            if summa > 3 and old_board.is_alive(cell):
                self.board.set_alive(cell, False)
            for neighbor in dead_cells:
                n_summa, _ = self.check_area(old_board, neighbor)
                if n_summa == 3 and not old_board.is_alive(neighbor):
                    self.board.set_alive(neighbor, True)
        self.sequence.append(old_board)
        self.board.calc_area()

    def _boards_equal(self, board_a, board_b):
        return board_a.live_cells == board_b.live_cells

    def check_if_changed(self):
        for period in range(1, MAX_DETECTED_PERIOD + 1):
            if len(self.sequence) >= period:
                if self._boards_equal(self.board, self.sequence[-period]):
                    return False
        return True

    def initialize_board(self):
        if self.rand_rate:
            self.board.add_random_coords(rate=self.rand_rate)
        self.board.calc_area()
        self._initial_board = copy.deepcopy(self.board)
        self.sequence = []

    def step_back(self):
        """Restore the previous generation. Returns False if already at the start."""
        while self.sequence and self._boards_equal(self.board, self.sequence[-1]):
            self.sequence.pop()
        if self.sequence:
            self.board = copy.deepcopy(self.sequence.pop())
            self.board.calc_area()
            return True
        if self._boards_equal(self.board, self._initial_board):
            return False
        self.board = copy.deepcopy(self._initial_board)
        self.board.calc_area()
        return True

    def step(self):
        """Advance one generation. Returns False when the run should stop."""
        self.advance_board()
        if not self.check_if_changed():
            self.sequence.append(self.board)
            return False
        return True

    def run_simulation(self, verbose=True):
        self.initialize_board()
        if verbose:
            if hasattr(self.board, "print_board"):
                self.board.print_board()
            self.board.print_area()
        for i in range(self.max_iter):
            if not self.step():
                if verbose:
                    print(
                        "- Stopped at generation {0} (repeating pattern).".format(i)
                    )
                break
            if verbose:
                print(
                    "- Generation {0}. - maximum iteration: {1}".format(
                        i, self.max_iter
                    )
                )
        else:
            if verbose:
                print("- Stopped at max iteration {0}.".format(self.max_iter))


def make_game(
    topology,
    board_size=64,
    frequency=8,
    neighborhood=8,
    max_iter=2500,
    rand_rate=0.5,
):
    """Factory for flat or geodesic games."""
    from topology import Topology

    if topology == Topology.SPHERE:
        board = GeodesicBoard(frequency)
        return GameOfLife(board, rule_set=None, max_iter=max_iter, rand_rate=rand_rate)

    rules = Rules(
        neighborhood,
        board_size,
        toroidal=(topology == Topology.TOROIDAL),
    )
    board = FlatBoard(board_size, rules=rules)
    return GameOfLife(board, rule_set=rules, max_iter=max_iter, rand_rate=rand_rate)


def main():
    from ui.pygame_app import run_pygame_app

    run_pygame_app(
        board_size=64,
        neighborhood=8,
        max_iter=2500,
        rand_rate=0.50,
    )


if __name__ == "__main__":
    main()
