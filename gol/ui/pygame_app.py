from typing import Any

import pygame

from ..game import make_game
from ..topology import Topology
from .colors import COLOR_ACCENT, COLOR_ALIVE, COLOR_BG, COLOR_DEAD, COLOR_GRID_LINE
from .grid_renderer import draw_grid
from .layout import (
    BOARD_SIZE_MAX,
    BOARD_SIZE_MIN,
    BOARD_SIZE_STEP,
    DEFAULT_FPS,
    DEFAULT_STEPS_PER_FRAME,
    FREQUENCY_MAX,
    FREQUENCY_MIN,
    FREQUENCY_STEP,
    GRID_MARGIN_LEFT,
    GRID_PANEL_GAP,
    MAX_ITER_MAX,
    MAX_ITER_MIN,
    MAX_ITER_STEP,
    MIN_WINDOW_HEIGHT,
    PANEL_WIDTH,
    RAND_RATE_MAX,
    RAND_RATE_MIN,
    RAND_RATE_STEP,
    WINDOW_PAD_RIGHT,
    compute_initial_window_size,
    update_layout,
)
from .panels import draw_panel
from .sphere_renderer import SphereRenderer


_FONT_CANDIDATES = ("consolas", "menlo", "dejavu sans mono", "courier new")


def load_ui_font(size: int, bold: bool = False) -> pygame.font.Font:
    """Load a monospace UI font, falling back if Consolas is missing."""
    for name in _FONT_CANDIDATES:
        if pygame.font.match_font(name) is not None:
            return pygame.font.SysFont(name, size, bold=bold)
    return pygame.font.Font(None, size)


class PygameApp(object):

    def __init__(
        self,
        board_size: int = 64,
        neighborhood: int = 8,
        max_iter: int = 2500,
        rand_rate: float = 0.5,
        toroidal: bool = False,
        topology: Topology | None = None,
        frequency: int = 8,
        fps: int = DEFAULT_FPS,
    ) -> None:
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

        self._config_buttons: list[dict[str, Any]] = []
        self._start_button_rect = None
        self.sphere_renderer = SphereRenderer(
            color_alive=COLOR_ALIVE,
            color_dead=COLOR_DEAD,
            color_edge=COLOR_GRID_LINE,
            color_accent=COLOR_ACCENT,
        )

        pygame.init()
        self.font = load_ui_font(16)
        self.font_title = load_ui_font(20, bold=True)
        self.font_small = load_ui_font(14)

        self.game = self._make_game()
        self.window_width, self.window_height = compute_initial_window_size(
            self._is_sphere, self.board_size
        )
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

    def _init_display(self):
        self.screen = pygame.display.set_mode(
            (self.window_width, self.window_height), pygame.RESIZABLE
        )

    def _update_layout(self):
        update_layout(self)

    def _dec_board_size(self):
        if self._is_sphere:
            self.frequency = max(FREQUENCY_MIN, self.frequency - FREQUENCY_STEP)
        else:
            self.board_size = max(BOARD_SIZE_MIN, self.board_size - BOARD_SIZE_STEP)
        self.apply_config()

    def _inc_board_size(self):
        if self._is_sphere:
            self.frequency = min(FREQUENCY_MAX, self.frequency + FREQUENCY_STEP)
        else:
            self.board_size = min(BOARD_SIZE_MAX, self.board_size + BOARD_SIZE_STEP)
        self.apply_config()

    def _dec_neighborhood(self):
        if not self._is_sphere:
            self.neighborhood = 4
        self.apply_config()

    def _inc_neighborhood(self):
        if not self._is_sphere:
            self.neighborhood = 8
        self.apply_config()

    def _dec_topology(self):
        self.topology = self.topology.prev()
        self.apply_config()

    def _inc_topology(self):
        self.topology = self.topology.next()
        self.apply_config()

    def _dec_max_iter(self):
        self.max_iter = max(MAX_ITER_MIN, self.max_iter - MAX_ITER_STEP)
        self.apply_config()

    def _inc_max_iter(self):
        self.max_iter = min(MAX_ITER_MAX, self.max_iter + MAX_ITER_STEP)
        self.apply_config()

    def _dec_rand_rate(self):
        self.rand_rate = round(
            max(RAND_RATE_MIN, self.rand_rate - RAND_RATE_STEP), 2
        )
        self.apply_config()

    def _inc_rand_rate(self):
        self.rand_rate = round(
            min(RAND_RATE_MAX, self.rand_rate + RAND_RATE_STEP), 2
        )
        self.apply_config()

    def apply_config(self):
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
                return
            if row["plus"].collidepoint(pos):
                row["on_inc"]()
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

    def _draw(self):
        self.screen.fill(COLOR_BG)
        if self._is_sphere:
            self.sphere_renderer.draw(
                self.screen, self.game.board, self.grid_rect
            )
        else:
            draw_grid(
                self.screen, self.game.board, self.grid_rect, self.cell_size
            )
        draw_panel(self)
        pygame.display.flip()

    def run(self):
        while self._running:
            self._handle_events()
            self._simulate_steps()
            self._draw()
            self.clock.tick(self.fps)
        pygame.quit()


def run_pygame_app(
    board_size: int = 64,
    neighborhood: int = 8,
    max_iter: int = 2500,
    rand_rate: float = 0.5,
    toroidal: bool = False,
    topology: Topology | None = None,
    frequency: int = 8,
    fps: int = DEFAULT_FPS,
) -> None:
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
