import pygame

# Layout: grid on the left, side panel for stats and controls.
PANEL_WIDTH = 480
GRID_MARGIN_LEFT = 20
GRID_MARGIN_TOP = 20
GRID_PANEL_GAP = 10
WINDOW_PAD_RIGHT = 8
WINDOW_HEIGHT = 640
GRID_MARGIN_BOTTOM = 20
MIN_WINDOW_WIDTH = (
    GRID_MARGIN_LEFT + 80 + GRID_PANEL_GAP + PANEL_WIDTH + WINDOW_PAD_RIGHT
)
MIN_WINDOW_HEIGHT = WINDOW_HEIGHT
DEFAULT_FPS = 15
DEFAULT_STEPS_PER_FRAME = 1

BOARD_SIZE_MIN = 16
BOARD_SIZE_MAX = 128
BOARD_SIZE_STEP = 8

FREQUENCY_MIN = 4
FREQUENCY_MAX = 16
FREQUENCY_STEP = 2

MAX_ITER_MIN = 100
MAX_ITER_MAX = 10000
MAX_ITER_STEP = 100

RAND_RATE_MIN = 0.0
RAND_RATE_MAX = 1.0
RAND_RATE_STEP = 0.05

BUTTON_W = 32
BUTTON_H = 26
BUTTON_GAP = 6
VALUE_BUTTON_GAP = 12
ROW_HEIGHT = 40
CONFIG_ROW_START_Y = 108
CONFIG_PAD = 16
START_BUTTON_H = 36


def compute_initial_window_size(is_sphere, board_size):
    """One-time startup sizing to match pre-resize defaults."""
    if is_sphere:
        grid_pixels = min(WINDOW_HEIGHT - 40, 520)
    else:
        baseline_cell = max(
            4,
            min(12, (WINDOW_HEIGHT - 40) // board_size),
        )
        grid_pixels = board_size * baseline_cell
    window_height = max(
        WINDOW_HEIGHT,
        grid_pixels + GRID_MARGIN_TOP + GRID_MARGIN_BOTTOM,
    )
    window_width = (
        GRID_MARGIN_LEFT
        + grid_pixels
        + GRID_PANEL_GAP
        + PANEL_WIDTH
        + WINDOW_PAD_RIGHT
    )
    return window_width, window_height


def config_row_layout(panel_rect, row_y):
    x_label = panel_rect.x + CONFIG_PAD
    x_plus = panel_rect.right - CONFIG_PAD - BUTTON_W
    x_minus = x_plus - BUTTON_GAP - BUTTON_W
    return x_label, x_minus, x_plus


def build_config_buttons(app):
    app._config_buttons = []
    x_label = app.panel_rect.x + CONFIG_PAD
    y = CONFIG_ROW_START_Y

    rows = [
        ("board_size", app._dec_board_size, app._inc_board_size),
        ("neighborhood", app._dec_neighborhood, app._inc_neighborhood),
        ("topology", app._dec_topology, app._inc_topology),
        ("max_iter", app._dec_max_iter, app._inc_max_iter),
        ("rand_rate", app._dec_rand_rate, app._inc_rand_rate),
    ]
    for key, on_dec, on_inc in rows:
        _, x_minus, x_plus = config_row_layout(app.panel_rect, y)
        minus_rect = pygame.Rect(x_minus, y, BUTTON_W, BUTTON_H)
        plus_rect = pygame.Rect(x_plus, y, BUTTON_W, BUTTON_H)
        app._config_buttons.append({
            "key": key,
            "label_x": x_label,
            "minus": minus_rect,
            "plus": plus_rect,
            "on_dec": on_dec,
            "on_inc": on_inc,
        })
        y += ROW_HEIGHT

    start_w = app.panel_rect.width - 2 * CONFIG_PAD
    app._start_button_rect = pygame.Rect(
        x_label,
        y + 8,
        start_w,
        START_BUTTON_H,
    )


def update_layout(app):
    panel_left = app.window_width - PANEL_WIDTH - WINDOW_PAD_RIGHT
    app.panel_rect = pygame.Rect(
        panel_left, 0, PANEL_WIDTH, app.window_height
    )

    avail_w = panel_left - GRID_MARGIN_LEFT - GRID_PANEL_GAP
    avail_h = app.window_height - GRID_MARGIN_TOP - GRID_MARGIN_BOTTOM
    grid_side = max(1, min(avail_w, avail_h))
    app.grid_rect = pygame.Rect(
        GRID_MARGIN_LEFT, GRID_MARGIN_TOP, grid_side, grid_side
    )

    if not app._is_sphere:
        app.cell_size = max(1, app.grid_rect.width // app.board_size)

    build_config_buttons(app)
