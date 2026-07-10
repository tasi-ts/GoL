# Pygame UI (`ui/pygame_app.py`)

Real-time viewer for the active `src/` implementation. Uses **pygame-ce** (`pip install pygame-ce`; `import pygame` in code). Replaces the legacy post-run matplotlib animation.

## Layout

```text
┌─────────────────────────────┬──────────────────┐
│                             │  Title + stats   │
│   Grid (2D) or Sphere (3D)  │  Generation      │
│                             │  Population      │
│                             │  Status          │
│                             │  Speed / FPS     │
│                             │  Key hints       │
└─────────────────────────────┴──────────────────┘
```

Constants in `pygame_app.py`:

| Constant | Default | Purpose |
|----------|---------|---------|
| `PANEL_WIDTH` | 480 | Right column width for stats and controls (fixed; right-anchored) |
| `DEFAULT_FPS` | 15 | Default FPS cap |
| `WINDOW_HEIGHT` | 640 | Minimum window height |
| `MIN_WINDOW_WIDTH` / `MIN_WINDOW_HEIGHT` | derived / 640 | Smallest allowed window when resizing |
| `FREQUENCY_MIN` / `MAX` / `STEP` | 4 / 16 / 2 | Geodesic frequency range |

`grid_rect` holds the board view (2D grid or 3D sphere); `panel_rect` is the fixed 480px column anchored to the right edge of the window.

### Window resize and zoom

The window is **resizable** (`pygame.RESIZABLE`). Dragging edges changes only the left game viewport:

- **Right panel** stays 480px wide, glued to the right; button sizes, fonts, and layout do not scale.
- **Left grid view** grows or shrinks; in 2D modes `cell_size` is recalculated as `grid_rect.width // board_size` (minimum 1px per cell), so resize acts as zoom in/out.
- **Board config changes** (board size, topology, frequency) call `_update_layout()` only — the OS window size is unchanged; cells rescale within the existing viewport.
- **Sphere mode** uses the full `grid_rect` for projection; `[` / `]` zoom is additive on top of viewport size.

On first launch, `_compute_initial_window_size()` preserves the previous default dimensions (1094×640 for a 64×64 board).

## `PygameApp`

- Opens **paused** in **setup** mode (`_simulation_started = False`). Config is editable until **Start** or **Enter**.
- **`start_simulation()`** — seeds via `initialize_board()`, locks config, stays paused.
- **`reset_to_setup()`** — clears run state; config editable again (**R**).
- **`_draw_config_panel()`** — +/- buttons for board size / frequency, neighborhood (4/8), topology (Bounded / Toroidal / Sphere), max generations, random rate.
- **`_draw_running_panel()`** — generation, population, status, locked settings summary.
- **`run()`** — event loop: handle input → simulate → draw → `clock.tick(fps)`.

Simulation advances via `game.step()` only after Start, when not paused and not finished.

### Topology modes

| Topology | View | Board size row |
|----------|------|----------------|
| Bounded | 2D grid | Board size (16–128) |
| Toroidal | 2D grid | Board size (16–128) |
| Sphere | 3D mesh (`SphereRenderer`) | Frequency ν (4–16); shows cell count 10ν²+2 |

In **Sphere** mode the neighborhood row is grayed out (mesh adjacency is always used).

## Keyboard controls

Defined in **`PygameApp._handle_events()`**. Left/Right call **`_pause_for_scrub()`** first (sets `paused = True`), then **`_step_back()`** / **`_step_forward()`**.

| Key / UI | Handler | Effect |
|----------|---------|--------|
| +/- buttons (setup) | `_handle_config_click` | Adjust locked-until-start settings |
| Start / Enter | `start_simulation()` | Begin run (paused) |
| Left | `_step_back()` | One generation back (after Start) |
| Right | `_step_forward()` | One generation forward (after Start) |
| Space | — | Pause / resume (after Start) |
| R | `reset_to_setup()` | Back to setup screen |
| +/- keys | — | Steps per frame (after Start) |
| Up/Down | — | FPS cap |
| Drag on grid (Sphere) | `SphereRenderer` | Rotate view |
| `[` / `]` (Sphere) | `SphereRenderer` | Zoom (additive to viewport size) |
| Window resize | `_update_layout()` | Zoom 2D grid / rescale sphere viewport; panel unchanged |
| Esc / Q | — | Quit |

Frame scrubbing uses `game.sequence` and `game._initial_board` (see `step_back()` in `game.py`).

## `run_pygame_app(...)`

Convenience entry used from `game.main()`:

```python
run_pygame_app(
    board_size=64,
    neighborhood=8,
    max_iter=2500,
    rand_rate=0.5,
    topology=Topology.BOUNDED,
    frequency=8,
    fps=30,
)
```

`toroidal=True` still maps to `Topology.TOROIDAL` for backward compatibility.

## Extending the panel

Add widgets by drawing into `panel_rect` and handling clicks in `_handle_events()` (hit-test `pygame.Rect` regions). Keep Conway logic in `game.py` / `board.py` / `rules.py` with no `pygame` imports.

## Dependencies

- **pygame-ce** `>=2.5.0` — install with `pip install pygame-ce`; import as `import pygame` (drop-in API). Community-maintained fork with pre-built wheels for current Python versions.
- **numpy** (geodesic mesh and sphere renderer)
