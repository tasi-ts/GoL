from collections import deque
from collections.abc import Iterable
from typing import Any, Generic

from .board import BoardProtocol, FlatBoard
from .geodesic_board import GeodesicBoard
from .rules import Rules
from .topology import Topology
from .types import CellT

MAX_DETECTED_PERIOD = 6
BIRTH = frozenset({3})
SURVIVE = frozenset({2, 3})


class GameOfLife(Generic[CellT]):

    def __init__(
        self,
        init_board: BoardProtocol[CellT],
        rule_set: Rules | None = None,
        max_iter: int = 2500,
        rand_rate: float = 0.5,
        seed: int | None = None,
    ) -> None:
        self.board = init_board
        if isinstance(init_board, FlatBoard) and rule_set is not None:
            init_board.rules = rule_set
        self.rule_set = rule_set
        self.max_iter = max_iter
        self.rand_rate = rand_rate
        self.seed = seed
        self._history: list[frozenset[CellT]] = []
        self._period_window: deque[frozenset[CellT]] = deque(
            maxlen=MAX_DETECTED_PERIOD
        )
        self._initial_live: frozenset[CellT] = frozenset()

    @property
    def sequence(self) -> list[frozenset[CellT]]:
        """Previous-generation live-cell snapshots (for tests and scrubbing)."""
        return self._history

    def _neighbor_stats(
        self, live: set[CellT], cell: CellT
    ) -> tuple[int, set[CellT]]:
        live_count = 0
        dead_neighbors: set[CellT] = set()
        for neighbor in self.board.neighbors(cell):
            if neighbor in live:
                live_count += 1
            else:
                dead_neighbors.add(neighbor)
        return live_count, dead_neighbors

    def _restore_live(self, live: Iterable[CellT]) -> None:
        self.board.cells.clear()
        self.board.cells.update(live)

    def _record_snapshot(self, live: set[CellT]) -> None:
        snapshot = frozenset(live)
        self._history.append(snapshot)
        self._period_window.append(snapshot)

    def advance_board(self) -> None:
        old_live = set(self.board.live_cells)
        deaths: set[CellT] = set()
        birth_candidates: set[CellT] = set()
        for cell in old_live:
            live_count, dead_neighbors = self._neighbor_stats(old_live, cell)
            if live_count not in SURVIVE:
                deaths.add(cell)
            birth_candidates.update(dead_neighbors)

        births: set[CellT] = set()
        for cell in birth_candidates:
            live_count, _ = self._neighbor_stats(old_live, cell)
            if live_count in BIRTH:
                births.add(cell)

        for cell in deaths:
            self.board.set_alive(cell, False)
        for cell in births:
            self.board.set_alive(cell, True)
        self._record_snapshot(old_live)

    def check_if_changed(self) -> bool:
        current = self.board.live_cells
        for period in range(1, MAX_DETECTED_PERIOD + 1):
            if len(self._period_window) >= period:
                if current == self._period_window[-period]:
                    return False
        return True

    def initialize_board(self) -> None:
        if self.rand_rate > 0:
            self.board.add_random_coords(rate=self.rand_rate, seed=self.seed)
        self._initial_live = frozenset(self.board.live_cells)
        self._history = []
        self._period_window = deque(maxlen=MAX_DETECTED_PERIOD)

    def step_back(self) -> bool:
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

    def step(self) -> bool:
        """Advance one generation. Returns False when the run should stop."""
        self.advance_board()
        if not self.check_if_changed():
            return False
        return True

    def run_simulation(self, verbose: bool = True) -> None:
        self.initialize_board()
        if verbose:
            print_board = getattr(self.board, "print_board", None)
            if callable(print_board):
                print_board()
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


def apply_pattern(game: GameOfLife[Any], cells: Iterable[Any]) -> None:
    """Place cells after ``initialize_board`` with ``rand_rate=0``.

    Updates the scrub origin so Left at generation 0 keeps the pattern.
    """
    game.board.add_object(cells)
    game._initial_live = frozenset(game.board.live_cells)


def make_game(
    topology: Topology,
    board_size: int = 64,
    frequency: int = 8,
    neighborhood: int = 8,
    max_iter: int = 2500,
    rand_rate: float = 0.5,
    seed: int | None = None,
) -> GameOfLife[Any]:
    """Factory for flat or geodesic games."""
    if topology == Topology.SPHERE:
        return GameOfLife(
            GeodesicBoard(frequency),
            rule_set=None,
            max_iter=max_iter,
            rand_rate=rand_rate,
            seed=seed,
        )

    rules = Rules(
        neighborhood,
        board_size,
        toroidal=(topology == Topology.TOROIDAL),
    )
    return GameOfLife(
        FlatBoard(board_size, rules=rules),
        rule_set=rules,
        max_iter=max_iter,
        rand_rate=rand_rate,
        seed=seed,
    )


def main() -> None:
    from .cli import main as cli_main

    cli_main()


if __name__ == "__main__":
    main()
