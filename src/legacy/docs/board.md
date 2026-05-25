# `board.py` — Grid state and visualization helpers

**File:** [`../board.py`](../board.py)

The `Board` class is the **single source of truth** for the cellular automaton state on a finite `size × size` grid. It maintains redundant representations for convenience and consistency checking.

## Dual representation

| Attribute | Type | Role |
|-----------|------|------|
| `size` | `int` | Board width and height (square grid) |
| `array` | `list[list[int]]` | Full grid; `0` = dead, `1` = alive |
| `cells` | `set` of `(x, y)` | Live cell coordinates only |
| `area` | `int` | Count of live cells (must match sum of `array`) |

Every mutation that affects live cells should update **both** `array` and `cells`, then call `calc_area()` to refresh `area` and verify consistency.

## Constructor

```python
Board(size)
```

Creates an empty board: all zeros in `array`, empty `cells`, `area = 0`.

## Display and export

### `print_board()`

Prints the full grid to stdout, one row per line, space-separated `0`/`1` values. Used at the start of `run_simulation()`.

### `print_cells()` / `print_area()`

Debug helpers: print the live-cell set or the line `Area: {area}`. Commented out in the default game loop but available for inspection.

### `convert_to_binary_image()`

Returns a `size × size` nested list for matplotlib: live cells become **255**, dead cells **0**. The implementation transposes indices when building the image (`array[j][i]`), so the visual orientation may differ from row-major console printing—worth noting when comparing console output to the animation.

### `display_board()`

Opens a static matplotlib window for the current state (`imshow` + `show`). Not used in the default `game.py` flow.

## Seeding patterns

### `add_object(coord_set)`

Sets all coordinates in `coord_set` to alive:

- Unions `coord_set` into `cells`.
- Sets `array[x][y] = 1` for each `(x, y)`.
- Calls `calc_area()`.

Use this for known patterns (gliders, blocks, etc.) if you extend `main()` beyond random seeds.

### `add_random_coords(rate=None)`

Fills the board with random live cells:

| `rate` | Behavior |
|--------|----------|
| `None` | Target count = `int(size * size * 0.5)` (~50% density) |
| float e.g. `0.5` | Target count = `int(size * size * rate)` |

Algorithm: repeatedly pick random `(x, y)` until the target count of **distinct** live cells is reached (skips duplicates). Then `calc_area()`.

Called from `GameOfLife.run_simulation()` when `rand_rate` is truthy (default `0.5` in `main()`).

## Integrity: `calc_area()`

1. `area_array` = sum of all values in `array` (count of 1s).
2. `area_cells` = `len(self.cells)`.
3. If they differ, raises `Exception("--- Area is inconsistent! ---")`.
4. Otherwise sets `self.area = area_cells`.

This catches bugs where `array` and `cells` diverge—important because `game.py` updates both during evolution.

## Dependencies

- **`random`** — `add_random_coords`
- **`matplotlib.pyplot`** — `display_board` only

## Relationship to other modules

- **`Rules`** must use the same `size` as the board so neighbor lookups stay in bounds.
- **`GameOfLife`** deep-copies `Board` instances into `sequence` each generation for history and animation.
