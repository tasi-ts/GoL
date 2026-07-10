# Geodesic sphere topology

**Files:** [`../geodesic_mesh.py`](../geodesic_mesh.py), [`../geodesic_board.py`](../geodesic_board.py), [`../ui/sphere_renderer.py`](../ui/sphere_renderer.py)

Sphere mode runs Conway's Game of Life on a **geodesic Goldberg polyhedron** — a class-I icosahedral subdivision projected onto the unit sphere. Cells are mesh vertices; neighbors are fixed by mesh adjacency (degree 5 or 6).

## Mesh (`GeodesicMesh`)

### Frequency

Subdivision **frequency** `ν` controls resolution:

| ν | Cell count (10ν² + 2) |
|---|----------------------|
| 4 | 162 |
| 8 | 642 |
| 16 | 2562 |

The UI repurposes the board-size row as **Frequency** when topology is **Sphere** (ν ∈ {4, 6, 8, …, 16}).

### Construction

1. Start from a unit icosahedron (12 vertices, 20 faces).
2. Subdivide each triangular face `ν` times; interpolate barycentrically and project onto the sphere.
3. Treat each mesh **vertex** as a cell (dual Goldberg face).
4. Two cells are neighbors when their vertices share a mesh edge.

Result:

- **12 pentagonal** cells (original icosahedron vertices)
- **10ν² − 10 hexagonal** cells
- **10ν² + 2** total cells

### Stored data

- `vertices` — unit-sphere positions (`numpy` array)
- `adjacency` — `list[set[int]]` neighbor ids per cell
- `cell_polygons` — spherical polygon per cell for 3D rendering
- `cell_centers` — same as `vertices` (used for depth sorting)

## Board (`GeodesicBoard`)

Implements the shared board protocol:

| Method / property | Sphere semantics |
|-------------------|------------------|
| `live_cells` | `set[int]` of alive cell ids |
| `is_alive(cell)` | membership test |
| `neighbors(cell)` | mesh adjacency |
| `add_random_coords(rate)` | random fraction of all cell ids |

`__deepcopy__` shares the immutable `GeodesicMesh` and copies only the `alive` set — efficient for `step_back` / period detection.

## Rules on the sphere

Sphere mode does **not** use offset-based `Rules`. Neighborhood 4/8 is meaningless on a geodesic mesh; the UI grays out that control. Conway **B3/S23** still applies using full mesh adjacency.

## 3D rendering (`SphereRenderer`)

Drawn into the same `grid_rect` as the flat grid:

- Orthographic projection with yaw/pitch rotation
- Painter's algorithm (depth-sorted polygons)
- Alive/dead colors match the flat UI

### Camera (sphere mode)

| Input | Effect |
|-------|--------|
| Mouse drag (LMB) on grid | Rotate yaw / pitch |
| `[` / `]` | Zoom out / in |
| Scroll wheel on grid | Zoom |

## Factory

`game.make_game(topology=Topology.SPHERE, frequency=8, ...)` builds a `GeodesicBoard` with `rule_set=None`.

```python
from topology import Topology
from game import make_game

game = make_game(Topology.SPHERE, frequency=8, max_iter=500, rand_rate=0.3)
game.initialize_board()
game.step()
```
