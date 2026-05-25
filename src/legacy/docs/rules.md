# `rules.py` — Neighborhood and grid bounds

**File:** [`../rules.py`](../rules.py)

The `Rules` class does **not** encode Conway's birth/survival logic. It only defines **which adjacent cells count as neighbors** for a coordinate on a **square, bounded** grid of a given `size`. Conway's B3/S23 rules are applied in `game.py` after neighbor counts are computed.

## Class: `Rules`

### Constructor

```python
Rules(neighborhood, size)
```

| Parameter | Meaning |
|-----------|---------|
| `neighborhood` | `4` (von Neumann: up/down/left/right) or `8` (Moore: includes diagonals) |
| `size` | Edge length of the square grid (used for bounds checks) |

On init, `self.neighbors` is set to an empty `set()`; it is repopulated on each call to `calc_neighbors`.

### Properties with validation

**`neighborhood`** (getter/setter)

- Allowed values: **4** or **8** only.
- Any other value raises `ValueError("--- Neighborhood must be 4 or 8! ---")`.

**`size`** (getter/setter)

- Must be **greater than 2**.
- Otherwise raises `ValueError("--- Size must be greater than 2! ---")`.

Setters store values in `_neighborhood` and `_size`; getters return those private fields.

### Method: `calc_neighbors(x, y)`

**Purpose:** Fill `self.neighbors` with all neighbor coordinates of `(x, y)` that lie inside the grid `[0, size) × [0, size)`.

**Behavior step by step:**

1. Reset `self.neighbors` to `set()`.
2. If `x >= size` or `y >= size`, return immediately (invalid coordinate guard).
3. **4-neighbor core** (used when `neighborhood` is 4 or 8):
   - `(x-1, y)` if `x-1 >= 0`
   - `(x+1, y)` if `x+1 < size`
   - `(x, y-1)` if `y-1 >= 0`
   - `(x, y+1)` if `y+1 < size`
4. **Diagonal neighbors** (only when `neighborhood == 8`):
   - `(x±1, y±1)` with the same boundary checks on each index.

Coordinates use **(x, y)** as **row, column** indices into `Board.array[x][y]`, consistent with the rest of the legacy code.

**Note:** The condition `y >= 0` on horizontal neighbors is redundant (always true for valid `y`) but does not change results.

### Usage in the simulation

`GameOfLife.check_area()` calls `self.rule_set.calc_neighbors(x, y)` and then iterates `self.rule_set.neighbors` to count live neighbors and collect dead neighbor cells for birth checks.

Default in `main()`:

```python
Rules(8, 64)  # Moore neighborhood on a 64×64 board
```

## Design rationale

Separating **topology** (who is adjacent) from **dynamics** (Conway rules in `advance_board`) keeps `rules.py` small and allows swapping 4- vs 8-neighbor counting without touching the game loop. A future extension could add toroidal wrap-around here; the current code uses **hard boundaries** only.

## Limitations

- No wrap-around at edges; corner and edge cells have fewer neighbors.
- `calc_neighbors` does not exclude the center cell `(x, y)` from the neighbor set (it only adds offsets, so the center is never included).
- Invalid `(x, y)` outside the board clears neighbors and returns without error.
