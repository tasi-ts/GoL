# `rules.py` — Neighborhood and grid bounds

**File:** [`../../gol/rules.py`](../../gol/rules.py)

The `Rules` class does **not** encode Conway's birth/survival logic. It only defines **which adjacent cells count as neighbors** for a coordinate on a **square grid** of a given `size`, with either **bounded** (hard edges) or **toroidal** (wrap-around) topology. Conway's B3/S23 rules are applied in `game.py` after neighbor counts are computed.

> **Sphere mode:** `Rules` is not used. Geodesic boards use fixed mesh adjacency (see [geodesic.md](geodesic.md)).

## Class: `Rules`

### Constructor

```python
Rules(neighborhood, size, toroidal=False)
```

| Parameter | Meaning |
|-----------|---------|
| `neighborhood` | `4` (von Neumann: up/down/left/right) or `8` (Moore: includes diagonals) |
| `size` | Edge length of the square grid (used for bounds checks and wrap) |
| `toroidal` | If `True`, edges wrap; if `False` (default), out-of-range neighbors are omitted |

On init, `self.neighbors` is set to an empty `set()`; it is repopulated on each call to `calc_neighbors`.

### Properties with validation

**`neighborhood`** (getter/setter)

- Allowed values: **4** or **8** only.
- Any other value raises `ValueError("--- Neighborhood must be 4 or 8! ---")`.

**`size`** (getter/setter)

- Must be **greater than 2**.
- Otherwise raises `ValueError("--- Size must be greater than 2! ---")`.

**`toroidal`** (getter/setter)

- Must be a **bool** (`True` or `False`).
- Otherwise raises `ValueError("--- Toroidal must be True or False! ---")`.

Setters store values in `_neighborhood`, `_size`, and `_toroidal`; getters return those private fields.

### Method: `calc_neighbors(x, y)`

**Purpose:** Fill `self.neighbors` with neighbor coordinates of `(x, y)` according to `neighborhood` and `toroidal`.

**Behavior step by step:**

1. Reset `self.neighbors` to `set()`.
2. If `(x, y)` is outside `[0, size) × [0, size)`, return immediately (invalid coordinate guard).
3. Build offset list: four orthogonal offsets; add four diagonals when `neighborhood == 8`.
4. For each offset `(dx, dy)`:
   - Compute `nx, ny = x + dx, y + dy`.
   - **Toroidal:** `nx %= size`, `ny %= size`, then add `(nx, ny)`.
   - **Bounded:** add `(nx, ny)` only if both indices are in `[0, size)`.

Coordinates use **(x, y)** as **row, column** indices into `Board.array[x][y]`, consistent with the rest of the legacy code.

On a toroidal board, every cell has exactly **4** or **8** neighbors (matching `neighborhood`). On a bounded board, edge and corner cells have fewer neighbors.

### Usage in the simulation

`GameOfLife` calls `board.neighbors(cell)` on flat boards, which delegates to `Rules.calc_neighbors`. On geodesic boards, neighbors come from the mesh directly.

Default in `main()`:

```python
Rules(8, 64)  # Moore neighborhood on a 64×64 bounded board
```

Toroidal example:

```python
Rules(8, 64, toroidal=True)
```

## Design rationale

Separating **topology** (who is adjacent) from **dynamics** (Conway rules in `advance_board`) keeps `rules.py` small and allows swapping 4- vs 8-neighbor counting or bounded vs toroidal boundaries without touching the game loop.

## Limitations

- Only **bounded** and **toroidal** topologies are supported for flat grids (sphere uses mesh adjacency; see [geodesic.md](geodesic.md)).
- `calc_neighbors` does not exclude the center cell `(x, y)` from the neighbor set (it only adds offsets, so the center is never included).
- Invalid `(x, y)` outside the board clears neighbors and returns without error.
