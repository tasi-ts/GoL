# Pygame UI (`ui/pygame_app.py`)

Real-time viewer for the active `src/` implementation. Replaces the legacy post-run matplotlib animation.

## Layout

```text
┌─────────────────────────────┬──────────────────┐
│                             │  Title + stats   │
│         Grid (scaled)       │  Generation      │
│                             │  Population      │
│                             │  Status          │
│                             │  Speed / FPS     │
│                             │  Key hints       │
│                             │  (future widgets)│
└─────────────────────────────┴──────────────────┘
```

Constants in `pygame_app.py`:

| Constant | Default | Purpose |
|----------|---------|---------|
| `PANEL_WIDTH` | 480 | Right column width for stats and controls |
| `DEFAULT_FPS` | 15 | Default FPS cap |
| `WINDOW_HEIGHT` | 640 | Minimum window height |
| `MIN_CELL_SIZE` / `MAX_CELL_SIZE` | 4 / 12 | Cell pixel size clamp |

`grid_rect` holds the board; `panel_rect` is everything to the right of the grid.

## `PygameApp`

- Opens **paused** in **setup** mode (`_simulation_started = False`). Config is editable until **Start** or **Enter**.
- **`start_simulation()`** — seeds via `initialize_board()`, locks config, stays paused.
- **`reset_to_setup()`** — clears run state; config editable again (**R**).
- **`_draw_config_panel()`** — +/- buttons for board size, neighborhood (4/8), max generations, random rate.
- **`_draw_running_panel()`** — generation, population, status, locked settings summary.
- **`run()`** — event loop: handle input → simulate → draw → `clock.tick(fps)`.

Simulation advances via `game.step()` only after Start, when not paused and not finished.

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
    fps=30,
)
```

## Extending the panel

Add widgets by drawing into `panel_rect` and handling clicks in `_handle_events()` (hit-test `pygame.Rect` regions). Keep Conway logic in `game.py` / `board.py` / `rules.py` with no `pygame` imports.

Optional later: **`pygame_gui`** for buttons and sliders without building a full PyQt app.

## Dependencies

- **pygame** `>=2.0.0,<2.1` (Python 3.6–compatible 2.0.x line)
