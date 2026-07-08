# `game.py` — Simulation engine and entry point

**File:** [`../game.py`](../game.py)

The `GameOfLife` class ties `Board` and `Rules` together: it applies **Conway's B3/S23 rules** each generation, records history, detects simple repetition, and drives the default **matplotlib** playback in `main()`.

## Imports

```python
from board import Board
from rules import Rules
```

Sibling imports require running `game.py` with `src/legacy` on the module path (see [README](README.md#running-the-simulation)).

## Class: `GameOfLife`

### Constructor

```python
GameOfLife(init_board, rule_set, max_iter, rand_rate=0.5)
```

| Attribute | Meaning |
|-----------|---------|
| `board` | Current `Board` instance |
| `rule_set` | `Rules` instance (neighborhood, size, and topology) |
| `max_iter` | Maximum generations in `run_simulation` |
| `rand_rate` | Fraction of cells to seed randomly; passed to `add_random_coords` |
| `sequence` | List of **previous** `Board` snapshots (deep copies), used for stop condition and animation |

### `check_area(array, x, y)`

Computes neighbor statistics for cell `(x, y)` on a **given** grid snapshot `array` (not necessarily the live `self.board`):

1. Calls `rule_set.calc_neighbors(x, y)`.
2. For each neighbor coordinate, reads `array[x][y]` (note: loop variable shadows `x, y` with neighbor indices).
3. Returns:
   - **`summa`** — count of live neighbors (value `1`).
   - **`dead_cells`** — set of dead neighbor coordinates (value `0`) considered for birth in `advance_board`.

### `advance_board()` — one Conway generation

Uses a **snapshot** `old_board = copy.deepcopy(self.board)` so all updates read the same previous generation (synchronous update).

**Phase 1 — update existing live cells**

For each `(x, y)` in `old_board.cells`:

1. `summa, dead_cells = check_area(old_board.array, x, y)`.
2. **Underpopulation:** if `summa < 2` and cell was alive → set dead, remove from `self.board.cells`.
3. **Overpopulation:** if `summa > 3` and cell was alive → set dead, remove from `self.board.cells`.
4. *(Survival with 2 or 3 neighbors leaves the cell unchanged.)*

**Phase 2 — births at dead neighbors**

For each `(dx, dy)` in `dead_cells` from step 1:

1. Recompute neighbors at `(dx, dy)` on `old_board`.
2. If `summa == 3` and `old_board.array[dx][dy] == 0` → birth: set alive and add to `self.board.cells`.

This only considers dead cells that were **neighbors of at least one live cell** in the old generation, which is sufficient on a finite grid: any cell with three live neighbors must be adjacent to a live cell.

**Phase 3 — bookkeeping**

- Appends `old_board` to `self.sequence`.
- Calls `self.board.calc_area()`.

**Implementation detail:** Phase 1 uses two separate `if` statements (not `elif`) for under- and over-population; a cell cannot match both. Removing from `self.board.cells` while iterating `old_board.cells` is safe because iteration is over the snapshot set.

### `MAX_DETECTED_PERIOD`

Module-level constant (default **6**). Maximum oscillation period detected by `check_if_changed()`—stable (period 1) through period 6.

### `_boards_equal(board_a, board_b)`

Returns whether two `Board` instances represent the same pattern: equal `cells` sets and equal `array` grids.

### `check_if_changed()`

Early-stop helper to avoid running all `max_iter` when the pattern **stabilizes** or **repeats** with period 1 through `MAX_DETECTED_PERIOD`.

For each `period` from **1** to `MAX_DETECTED_PERIOD` (checked in ascending order):

- If `len(self.sequence) >= period`, compare `self.board` to `self.sequence[-period]` via `_boards_equal`.
- On the first match, return **`False`** (stop simulation).

Returns **`True`** if no repeating period in that range is found.

| Period | Match condition | Meaning |
|--------|-----------------|--------|
| 1 | current == `sequence[-1]` | Still life (no change) |
| 2 | current == `sequence[-2]` | Period-2 oscillator |
| 3–6 | current == `sequence[-3]` … `sequence[-6]` | Longer oscillators |

Checking shorter periods first stops as early as possible (e.g. a stable board matches period 1 before later lags are tested).

When stop triggers, `run_simulation` appends the final `board` once more to `sequence`.

### `initialize_board()`

If `rand_rate` is truthy, calls `add_random_coords(rate=rand_rate)`, then `calc_area()`. Saves `_initial_board` and clears `sequence`. Used by the Pygame UI and `run_simulation()`.

### `step_back()`

Restores the previous generation from `sequence`, or `_initial_board` when at generation 1. Returns **`False`** at the start. Used by the Pygame UI (Left arrow).

### `step()`

Advances one generation (`advance_board()`), then `check_if_changed()`. Returns **`False`** when a repeating pattern is detected (and appends the final board to `sequence`); **`True`** otherwise.

### `run_simulation(verbose=True)`

Batch/console mode:

1. `initialize_board()`
2. If `verbose`, print initial board and area.
3. Loop up to `max_iter` calling `step()`; optional print per generation or stop message.

With default `rand_rate=0.5`, seeding always runs. Setting `rand_rate=0` skips random fill (falsy).

## `main()` — Pygame entry

Delegates to [`ui/pygame_app.py`](../ui/pygame_app.py) `run_pygame_app()` (real-time window). See [Pygame UI](ui.md).

```python
if __name__ == "__main__":
    main()
```

Legacy matplotlib replay remains in `src/legacy/game.py` only.

## Conway rules mapping (reference)

| Conway rule | Code location in `advance_board` |
|-------------|----------------------------------|
| Live, &lt; 2 neighbors → die | `summa < 2` and alive → clear cell |
| Live, 2–3 neighbors → survive | implicit (no change) |
| Live, &gt; 3 neighbors → die | `summa > 3` and alive → clear cell |
| Dead, exactly 3 neighbors → birth | `summa == 3` and dead → set cell |

## Dependencies

- **`copy.deepcopy`** — generation snapshots for period detection

UI dependency: **pygame** (see [ui.md](ui.md)). `board.display_board()` still uses matplotlib optionally.

## Possible extensions (not implemented)

- Configurable rule strings (e.g. HighLife B36/S23)
- CLI arguments for size, density, and iteration cap
- Ring buffer for `sequence` (only keep last `MAX_DETECTED_PERIOD` boards)
- Panel buttons via `pygame_gui` or similar
