import pygame

from ..game import make_game
from ..geodesic_mesh import GeodesicMesh
from ..topology import Topology
from .sphere_renderer import SphereRenderer


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

COLOR_BG = (24, 24, 28)
COLOR_PANEL = (32, 32, 38)
COLOR_PANEL_BORDER = (55, 55, 65)
COLOR_DEAD = (30, 30, 36)
COLOR_ALIVE = (0, 200, 120)
COLOR_GRID_LINE = (42, 42, 50)
COLOR_TEXT = (230, 230, 235)
COLOR_TEXT_DIM = (150, 150, 160)
COLOR_ACCENT = (0, 200, 120)
COLOR_BUTTON = (50, 50, 58)
COLOR_BUTTON_BORDER = (80, 80, 92)
COLOR_BUTTON_DISABLED = (40, 40, 46)
COLOR_START = (0, 140, 90)


class PygameApp(object):

    def __init__(
        self,
        board_size=64,
        neighborhood=8,
        max_iter=2500,
        rand_rate=0.5,
        toroidal=False,
        topology=None,
        frequency=8,
        fps=DEFAULT_FPS,
    ):
        self.board_size = board_size
        self.frequency = frequency
        self.neighborhood = neighborhood
        self.max_iter = max_iter
        self.rand_rate = rand_rate
        if topology is not None:
            self.topology = topology
        else:
            self.topology = Topology.from_toroidal(toroidal)
        self.fps = fps
        self.steps_per_frame = DEFAULT_STEPS_PER_FRAME

        self._simulation_started = False
        self.paused = True
        self.generation = 0
        self.status = "Configure settings, then Start"
        self._running = True
        self._finished = False

        self._config_buttons = []
        self._start_button_rect = None
        self.sphere_renderer = SphereRenderer(
            color_alive=COLOR_ALIVE,
            color_dead=COLOR_DEAD,
            color_edge=COLOR_GRID_LINE,
        )

        pygame.init()
        self.font = pygame.font.SysFont("consolas", 16)
        self.font_title = pygame.font.SysFont("consolas", 20, bold=True)
        self.font_small = pygame.font.SysFont("consolas", 14)

        self.game = self._make_game()
        self.window_width, self.window_height = self._compute_initial_window_size()
        self._init_display()
        self._update_layout()
        pygame.display.set_caption("Conway's Game of Life")
        self.clock = pygame.time.Clock()

    @property
    def _config_editable(self):
        return not self._simulation_started

    @property
    def _is_sphere(self):
        return self.topology == Topology.SPHERE

    def _make_game(self):
        return make_game(
            topology=self.topology,
            board_size=self.board_size,
            frequency=self.frequency,
            neighborhood=self.neighborhood,
            max_iter=self.max_iter,
            rand_rate=self.rand_rate,
        )

    def _compute_initial_window_size(self):
        """One-time startup sizing to match pre-resize defaults."""
        if self._is_sphere:
            grid_pixels = min(WINDOW_HEIGHT - 40, 520)
        else:
            baseline_cell = max(
                4,
                min(12, (WINDOW_HEIGHT - 40) // self.board_size),
            )
            grid_pixels = self.board_size * baseline_cell
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

    def _init_display(self):
        self.screen = pygame.display.set_mode(
            (self.window_width, self.window_height), pygame.RESIZABLE
        )

    def _update_layout(self):
        panel_left = self.window_width - PANEL_WIDTH - WINDOW_PAD_RIGHT
        self.panel_rect = pygame.Rect(
            panel_left, 0, PANEL_WIDTH, self.window_height
        )

        avail_w = panel_left - GRID_MARGIN_LEFT - GRID_PANEL_GAP
        avail_h = self.window_height - GRID_MARGIN_TOP - GRID_MARGIN_BOTTOM
        grid_side = max(1, min(avail_w, avail_h))
        self.grid_rect = pygame.Rect(
            GRID_MARGIN_LEFT, GRID_MARGIN_TOP, grid_side, grid_side
        )

        if not self._is_sphere:
            self.cell_size = max(1, self.grid_rect.width // self.board_size)

        self._build_config_buttons()

    def _config_row_layout(self, row_y):
        x_label = self.panel_rect.x + CONFIG_PAD
        x_plus = self.panel_rect.right - CONFIG_PAD - BUTTON_W
        x_minus = x_plus - BUTTON_GAP - BUTTON_W
        return x_label, x_minus, x_plus

    def _build_config_buttons(self):
        self._config_buttons = []
        x_label = self.panel_rect.x + CONFIG_PAD
        y = CONFIG_ROW_START_Y

        rows = [
            ("board_size", self._dec_board_size, self._inc_board_size),
            ("neighborhood", self._dec_neighborhood, self._inc_neighborhood),
            ("topology", self._dec_topology, self._inc_topology),
            ("max_iter", self._dec_max_iter, self._inc_max_iter),
            ("rand_rate", self._dec_rand_rate, self._inc_rand_rate),
        ]
        for key, on_dec, on_inc in rows:
            _, x_minus, x_plus = self._config_row_layout(y)
            minus_rect = pygame.Rect(x_minus, y, BUTTON_W, BUTTON_H)
            plus_rect = pygame.Rect(x_plus, y, BUTTON_W, BUTTON_H)
            self._config_buttons.append({
                "key": key,
                "label_x": x_label,
                "minus": minus_rect,
                "plus": plus_rect,
                "on_dec": on_dec,
                "on_inc": on_inc,
            })
            y += ROW_HEIGHT

        start_w = self.panel_rect.width - 2 * CONFIG_PAD
        self._start_button_rect = pygame.Rect(
            x_label,
            y + 8,
            start_w,
            START_BUTTON_H,
        )

    def _dec_board_size(self):
        if self._is_sphere:
            self.frequency = max(FREQUENCY_MIN, self.frequency - FREQUENCY_STEP)
        else:
            self.board_size = max(BOARD_SIZE_MIN, self.board_size - BOARD_SIZE_STEP)
        self._apply_config_change()

    def _inc_board_size(self):
        if self._is_sphere:
            self.frequency = min(FREQUENCY_MAX, self.frequency + FREQUENCY_STEP)
        else:
            self.board_size = min(BOARD_SIZE_MAX, self.board_size + BOARD_SIZE_STEP)
        self._apply_config_change()

    def _dec_neighborhood(self):
        if not self._is_sphere:
            self.neighborhood = 4

    def _inc_neighborhood(self):
        if not self._is_sphere:
            self.neighborhood = 8

    def _dec_topology(self):
        self.topology = self.topology.prev()
        self._apply_config_change()

    def _inc_topology(self):
        self.topology = self.topology.next()
        self._apply_config_change()

    def _dec_max_iter(self):
        self.max_iter = max(MAX_ITER_MIN, self.max_iter - MAX_ITER_STEP)

    def _inc_max_iter(self):
        self.max_iter = min(MAX_ITER_MAX, self.max_iter + MAX_ITER_STEP)

    def _dec_rand_rate(self):
        self.rand_rate = round(
            max(RAND_RATE_MIN, self.rand_rate - RAND_RATE_STEP), 2
        )

    def _inc_rand_rate(self):
        self.rand_rate = round(
            min(RAND_RATE_MAX, self.rand_rate + RAND_RATE_STEP), 2
        )

    def _apply_config_change(self):
        self.game = self._make_game()
        self._update_layout()

    def start_simulation(self):
        if self._simulation_started:
            return
        self.game = self._make_game()
        self.game.initialize_board()
        self._simulation_started = True
        self.generation = 0
        self._finished = False
        self.paused = True
        self.status = "Paused"

    def reset_to_setup(self):
        self._simulation_started = False
        self.generation = 0
        self._finished = False
        self.paused = True
        self.status = "Configure settings, then Start"
        self.game = self._make_game()

    def reset(self):
        self.reset_to_setup()

    def _handle_config_click(self, pos):
        if not self._config_editable:
            return
        if self._start_button_rect.collidepoint(pos):
            self.start_simulation()
            return
        for row in self._config_buttons:
            if row["minus"].collidepoint(pos):
                row["on_dec"]()
                if row["key"] in ("board_size", "topology"):
                    pass  # already applied in handler
                else:
                    self.game = self._make_game()
                return
            if row["plus"].collidepoint(pos):
                row["on_inc"]()
                if row["key"] in ("board_size", "topology"):
                    pass
                else:
                    self.game = self._make_game()
                return

    def _handle_events(self):
        for event in pygame.event.get():
            if self._is_sphere and self._simulation_started:
                self.sphere_renderer.handle_event(event, self.grid_rect)
            elif self._is_sphere and self._config_editable:
                self.sphere_renderer.handle_event(event, self.grid_rect)

            if event.type == pygame.QUIT:
                self._running = False
            elif event.type == pygame.VIDEORESIZE:
                min_grid = 80 if self._is_sphere else max(80, self.board_size)
                min_width = (
                    GRID_MARGIN_LEFT
                    + min_grid
                    + GRID_PANEL_GAP
                    + PANEL_WIDTH
                    + WINDOW_PAD_RIGHT
                )
                self.window_width = max(min_width, event.w)
                self.window_height = max(MIN_WINDOW_HEIGHT, event.h)
                self.screen = pygame.display.set_mode(
                    (self.window_width, self.window_height), pygame.RESIZABLE
                )
                self._update_layout()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_config_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self._running = False
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if self._config_editable:
                        self.start_simulation()
                elif event.key == pygame.K_SPACE:
                    if self._simulation_started and not self._finished:
                        self.paused = not self.paused
                        self.status = "Paused" if self.paused else "Running"
                elif event.key == pygame.K_r:
                    self.reset_to_setup()
                elif event.key in (pygame.K_EQUALS, pygame.K_PLUS):
                    if self._simulation_started:
                        self.steps_per_frame = min(64, self.steps_per_frame + 1)
                elif event.key == pygame.K_MINUS:
                    if self._simulation_started:
                        self.steps_per_frame = max(1, self.steps_per_frame - 1)
                elif event.key == pygame.K_UP:
                    self.fps = min(120, self.fps + 5)
                elif event.key == pygame.K_DOWN:
                    self.fps = max(1, self.fps - 5)
                elif event.key == pygame.K_LEFT:
                    if self._simulation_started:
                        self._pause_for_scrub()
                        self._step_back()
                elif event.key == pygame.K_RIGHT:
                    if self._simulation_started:
                        self._pause_for_scrub()
                        self._step_forward()

    def _pause_for_scrub(self):
        self.paused = True
        if self._finished and self.status.startswith("Stopped"):
            self.status = "Paused"

    def _step_back(self):
        if not self._simulation_started:
            return
        if self.game.step_back():
            self.generation = max(0, self.generation - 1)
            self._finished = False
            self.status = "Paused"
        else:
            self.status = "Paused (at start)"

    def _step_forward(self):
        if not self._simulation_started:
            return
        if self.generation >= self.game.max_iter:
            self.status = "Paused (max iterations reached)"
            return
        self._finished = False
        if not self.game.step():
            self._finished = True
            self.status = "Stopped (repeating pattern)"
        else:
            self.generation += 1
            if self.generation >= self.game.max_iter:
                self._finished = True
                self.status = "Stopped (max iterations)"
            else:
                self.status = "Paused"

    def _simulate_steps(self):
        if not self._simulation_started or self.paused or self._finished:
            return
        for _ in range(self.steps_per_frame):
            if self.generation >= self.game.max_iter:
                self._finished = True
                self.status = "Stopped (max iterations)"
                return
            if not self.game.step():
                self._finished = True
                self.status = "Stopped (repeating pattern)"
                return
            self.generation += 1

    def _draw_grid(self):
        board = self.game.board
        size = board.size
        cell = self.cell_size
        board_pixels = size * cell
        origin_x = self.grid_rect.x + (self.grid_rect.width - board_pixels) // 2
        origin_y = self.grid_rect.y + (self.grid_rect.height - board_pixels) // 2

        pygame.draw.rect(self.screen, COLOR_DEAD, self.grid_rect)
        for x in range(size):
            for y in range(size):
                if board.is_alive((x, y)):
                    pygame.draw.rect(
                        self.screen,
                        COLOR_ALIVE,
                        pygame.Rect(
                            origin_x + y * cell,
                            origin_y + x * cell,
                            cell,
                            cell,
                        ),
                    )

        if cell >= 6:
            for i in range(size + 1):
                x_pos = origin_x + i * cell
                y_pos = origin_y + i * cell
                pygame.draw.line(
                    self.screen,
                    COLOR_GRID_LINE,
                    (origin_x, y_pos),
                    (origin_x + size * cell, y_pos),
                    1,
                )
                pygame.draw.line(
                    self.screen,
                    COLOR_GRID_LINE,
                    (x_pos, origin_y),
                    (x_pos, origin_y + size * cell),
                    1,
                )

        pygame.draw.rect(self.screen, COLOR_ACCENT, self.grid_rect, 2)

    def _draw_button(self, rect, label, enabled=True, accent=False):
        fill = COLOR_START if accent else (
            COLOR_BUTTON if enabled else COLOR_BUTTON_DISABLED
        )
        pygame.draw.rect(self.screen, fill, rect)
        border = COLOR_ACCENT if accent else COLOR_BUTTON_BORDER
        pygame.draw.rect(self.screen, border, rect, 2)
        surf = self.font_small.render(label, True, COLOR_TEXT)
        tx = rect.x + (rect.width - surf.get_width()) // 2
        ty = rect.y + (rect.height - surf.get_height()) // 2
        self.screen.blit(surf, (tx, ty))

    def _board_size_label(self):
        if self._is_sphere:
            return "Frequency"
        return "Board size"

    def _board_size_value(self):
        if self._is_sphere:
            cells = GeodesicMesh.expected_cell_count(self.frequency)
            return "{0} ({1})".format(self.frequency, cells)
        return str(self.board_size)

    def _draw_config_panel(self):
        x = self.panel_rect.x + CONFIG_PAD
        y = 24
        title = self.font_title.render("Game of Life", True, COLOR_ACCENT)
        self.screen.blit(title, (x, y))
        y += 32

        hint = self.font_small.render(
            "Settings (before Start only)", True, COLOR_TEXT_DIM
        )
        self.screen.blit(hint, (x, y))
        y = CONFIG_ROW_START_Y

        labels = {
            "board_size": self._board_size_label(),
            "neighborhood": "Neighborhood",
            "topology": "Topology",
            "max_iter": "Max generations",
            "rand_rate": "Random rate",
        }
        values = {
            "board_size": self._board_size_value(),
            "neighborhood": str(self.neighborhood),
            "topology": self.topology.label(),
            "max_iter": str(self.max_iter),
            "rand_rate": "{0:.0%}".format(self.rand_rate),
        }

        for row in self._config_buttons:
            key = row["key"]
            row_y = row["minus"].y
            label_color = COLOR_TEXT_DIM if (
                key == "neighborhood" and self._is_sphere
            ) else COLOR_TEXT
            label_surf = self.font.render(labels[key], True, label_color)
            self.screen.blit(label_surf, (row["label_x"], row_y + 5))
            val_color = COLOR_TEXT_DIM if (
                key == "neighborhood" and self._is_sphere
            ) else COLOR_ACCENT
            val_surf = self.font.render(values[key], True, val_color)
            val_x = row["minus"].x - VALUE_BUTTON_GAP - val_surf.get_width()
            self.screen.blit(val_surf, (val_x, row_y + 5))
            neigh_enabled = self._config_editable and not (
                key == "neighborhood" and self._is_sphere
            )
            self._draw_button(
                row["minus"], "-", enabled=neigh_enabled
            )
            self._draw_button(
                row["plus"], "+", enabled=neigh_enabled
            )
            y = row_y + ROW_HEIGHT

        if self._start_button_rect:
            self._draw_button(
                self._start_button_rect,
                "Start",
                enabled=self._config_editable,
                accent=True,
            )

        y = self._start_button_rect.bottom + 24
        hints = [
            "Enter  also starts",
            "R      new setup",
            "Esc    quit",
        ]
        if self._is_sphere:
            hints.insert(1, "Drag   rotate sphere")
            hints.insert(2, "[ ]    zoom")
        for line in hints:
            surf = self.font_small.render(line, True, COLOR_TEXT_DIM)
            self.screen.blit(surf, (x, y))
            y += surf.get_height() + 4

    def _draw_running_panel(self):
        x = self.panel_rect.x + 16
        y = 24
        if self._is_sphere:
            board_line = "Frequency: {0}  Cells: {1}".format(
                self.frequency,
                GeodesicMesh.expected_cell_count(self.frequency),
            )
        else:
            board_line = "Board: {0}  Neighbor: {1}".format(
                self.board_size, self.neighborhood
            )

        lines = [
            ("Conway's Game of Life", self.font_title, COLOR_ACCENT),
            ("", self.font, COLOR_TEXT),
            ("Generation: {0}".format(self.generation), self.font, COLOR_TEXT),
            ("Population: {0}".format(self.game.board.area), self.font, COLOR_TEXT),
            ("Status: {0}".format(self.status), self.font, COLOR_TEXT),
            (board_line, self.font, COLOR_TEXT_DIM),
            ("Topology: {0}".format(self.topology.label()), self.font, COLOR_TEXT_DIM),
            ("Max gen: {0}  Seed: {1:.0%}".format(
                self.max_iter, self.rand_rate
            ), self.font, COLOR_TEXT_DIM),
            ("Speed: {0} step(s)/frame".format(self.steps_per_frame), self.font, COLOR_TEXT_DIM),
            ("FPS cap: {0}".format(self.fps), self.font, COLOR_TEXT_DIM),
            ("", self.font, COLOR_TEXT),
            ("Space  pause / resume", self.font, COLOR_TEXT_DIM),
            ("R      back to setup", self.font, COLOR_TEXT_DIM),
            ("+/-    steps per frame", self.font, COLOR_TEXT_DIM),
            ("Up/Dn  FPS cap", self.font, COLOR_TEXT_DIM),
            ("Left   step back (1 frame)", self.font, COLOR_TEXT_DIM),
            ("Right  step forward (1 frame)", self.font, COLOR_TEXT_DIM),
            ("Esc    quit", self.font, COLOR_TEXT_DIM),
        ]
        if self._is_sphere:
            lines.insert(-1, ("Drag   rotate  [ ] zoom", self.font, COLOR_TEXT_DIM))
        for text, font, color in lines:
            if not text:
                y += 8
                continue
            surf = font.render(text, True, color)
            self.screen.blit(surf, (x, y))
            y += surf.get_height() + 6

    def _draw_panel(self):
        pygame.draw.rect(self.screen, COLOR_PANEL, self.panel_rect)
        pygame.draw.line(
            self.screen,
            COLOR_PANEL_BORDER,
            (self.panel_rect.x, 0),
            (self.panel_rect.x, self.window_height),
            2,
        )
        if self._config_editable:
            self._draw_config_panel()
        else:
            self._draw_running_panel()

    def _draw(self):
        self.screen.fill(COLOR_BG)
        if self._is_sphere:
            self.sphere_renderer.draw(
                self.screen, self.game.board, self.grid_rect
            )
        else:
            self._draw_grid()
        self._draw_panel()
        pygame.display.flip()

    def run(self):
        while self._running:
            self._handle_events()
            self._simulate_steps()
            self._draw()
            self.clock.tick(self.fps)
        pygame.quit()


def run_pygame_app(
    board_size=64,
    neighborhood=8,
    max_iter=2500,
    rand_rate=0.5,
    toroidal=False,
    topology=None,
    frequency=8,
    fps=DEFAULT_FPS,
):
    if topology is None:
        topology = Topology.from_toroidal(toroidal)
    app = PygameApp(
        board_size=board_size,
        neighborhood=neighborhood,
        max_iter=max_iter,
        rand_rate=rand_rate,
        topology=topology,
        frequency=frequency,
        fps=fps,
    )
    app.run()
