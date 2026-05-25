# Conway's Game of Life

[Conway's Game of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life) is a **cellular automaton** devised by John Horton Conway in 1970. It is not a game in the usual sense—there are no players and no scoring— but a **dynamical system** on a grid that produces rich emergent patterns from very simple local rules.

## Grid and cells

- The world is a (usually infinite) **2D grid** of square **cells**.
- Each cell is in one of two states: **alive** or **dead** (in this project: `1` and `0`).
- Time advances in discrete steps called **generations** (or **ticks**). All cells update **simultaneously** from the state at the previous generation.

## The rules (B3/S23)

At each generation, consider the **eight neighbors** of a cell (orthogonal and diagonal—Moore neighborhood). The classic rules are:

| Condition | Result |
|-----------|--------|
| Live cell with **fewer than 2** live neighbors | **Dies** (underpopulation) |
| Live cell with **2 or 3** live neighbors | **Survives** |
| Live cell with **more than 3** live neighbors | **Dies** (overpopulation) |
| Dead cell with **exactly 3** live neighbors | **Becomes alive** (reproduction) |

These are often written as **B3/S23**: **B**irth on 3 neighbors, **S**urvival on 2 or 3 neighbors.

No other transitions occur: a dead cell with 0, 1, 2, 4, 5, 6, 7, or 8 neighbors stays dead; a live cell with exactly 2 or 3 neighbors stays alive.

## Common pattern types

- **Still lifes** — stable patterns that do not change (e.g. block, beehive).
- **Oscillators** — repeat every *n* generations (e.g. blinker, period 2).
- **Spaceships** — translate across the grid (e.g. glider).
- **Methuselahs** — small seeds that take many generations to stabilize.

This legacy code can **stop early** when it detects repetition with period **1 through 6** (see `MAX_DETECTED_PERIOD` in `game.py`).

## How this project maps to the rules

| Concept | In this codebase |
|---------|------------------|
| Grid | `Board.array` — `size × size`, values 0/1 |
| Live cells | `Board.cells` — set of `(x, y)` coordinates |
| Neighbors | `Rules.calc_neighbors(x, y)` — 8-connected by default in `main()` |
| One generation | `GameOfLife.advance_board()` |
| Initial pattern | `Board.add_random_coords(rate=...)` in `run_simulation()` |

The implementation uses a **finite** board with edges; Conway's original formulation is often described on an infinite plane. Border cells therefore behave differently than in an unbounded or toroidal world.

## Further reading

- [LifeWiki](https://conwaylife.com/wiki/)
- [Conway's Game of Life (Wikipedia)](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life)
