from collections import deque

from .board import FlatBoard
from .geodesic_board import GeodesicBoard
from .rules import Rules

MAX_DETECTED_PERIOD = 6
BIRTH = frozenset({3})
SURVIVE = frozenset({2, 3})


class GameOfLife:

    def __init__(
        self, init_board, rule_set=None, max_iter=2500, rand_rate=0.5, seed=None
    ) -> None:
        self.board = init_board
        if isinstance(init_board, FlatBoard) and rule_set is not None:
            init_board.rules = rule_set
        self.rule_set = rule_set
        self.max_iter = max_iter
        self.rand_rate = rand_rate
        self.seed = seed
        self._history = []
        self._period_window = deque(maxlen=MAX_DETECTED_PERIOD)
        self._initial_live = frozenset()

    @property
    def sequence(self):
        """Previous-generation live-cell snapshots (for tests and scrubbing)."""
        return self._history

    def _neighbor_stats(self, live, cell):
        live_count = 0
        dead_neighbors = set()
        for neighbor in self.board.neighbors(cell):
            if neighbor in live:
                live_count += 1
            else:
                dead_neighbors.add(neighbor)
        return live_count, dead_neighbors

    def _restore_live(self, live):
        self.board.cells.clear()
        self.board.cells.update(live)

    def _record_snapshot(self, live):
        snapshot = frozenset(live)
        self._history.append(snapshot)
        self._period_window.append(snapshot)

    def advance_board(self):
        old_live = set(self.board.live_cells)
        deaths = set()
        birth_candidates = set()
        for cell in old_live:
            live_count, dead_neighbors = self._neighbor_stats(old_live, cell)
            if live_count not in SURVIVE:
                deaths.add(cell)
            birth_candidates.update(dead_neighbors)

        births = set()
        for cell in birth_candidates:
            live_count, _ = self._neighbor_stats(old_live, cell)
            if live_count in BIRTH:
                births.add(cell)

        for cell in deaths:
            self.board.set_alive(cell, False)
        for cell in births:
            self.board.set_alive(cell, True)
        self._record_snapshot(old_live)

    def check_if_changed(self):
        current = self.board.live_cells
        for period in range(1, MAX_DETECTED_PERIOD + 1):
            if len(self._period_window) >= period:
                if current == self._period_window[-period]:
                    return False
        return True

    def initialize_board(self):
        if self.rand_rate > 0:
            self.board.add_random_coords(rate=self.rand_rate, seed=self.seed)
        self._initial_live = frozenset(self.board.live_cells)
        self._history = []
        self._period_window = deque(maxlen=MAX_DETECTED_PERIOD)

    def step_back(self):
        """Restore the previous generation. Returns False if already at the start."""
        while self._history and self.board.live_cells == self._history[-1]:
            self._history.pop()
        if self._history:
            self._restore_live(self._history.pop())
            self._period_window = deque(
                self._history[-MAX_DETECTED_PERIOD:], maxlen=MAX_DETECTED_PERIOD
            )
            return True
        if self.board.live_cells == self._initial_live:
            self._period_window = deque(maxlen=MAX_DETECTED_PERIOD)
            return False
        self._restore_live(self._initial_live)
        self._period_window = deque(maxlen=MAX_DETECTED_PERIOD)
        return True

    def step(self):
        """Advance one generation. Returns False when the run should stop."""
        self.advance_board()
        if not self.check_if_changed():
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
    seed=None,
):
    """Factory for flat or geodesic games."""
    from .topology import Topology

    if topology == Topology.SPHERE:
        board = GeodesicBoard(frequency)
        return GameOfLife(
            board, rule_set=None, max_iter=max_iter, rand_rate=rand_rate, seed=seed
        )

    rules = Rules(
        neighborhood,
        board_size,
        toroidal=(topology == Topology.TOROIDAL),
    )
    board = FlatBoard(board_size, rules=rules)
    return GameOfLife(
        board, rule_set=rules, max_iter=max_iter, rand_rate=rand_rate, seed=seed
    )


def main():
    from .ui.pygame_app import run_pygame_app

    run_pygame_app(
        board_size=64,
        neighborhood=8,
        max_iter=2500,
        rand_rate=0.50,
    )


if __name__ == "__main__":
    main()
