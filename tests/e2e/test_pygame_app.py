import pygame
import pytest

from gol.geodesic_board import GeodesicBoard
from gol.topology import Topology
from gol.ui.pygame_app import PygameApp
from tests.helpers import BLINKER_V, GLIDER

pytestmark = pytest.mark.e2e


def _post_key(key):
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {"key": key}))


def _click(pos):
    pygame.event.post(
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": pos, "button": 1})
    )


@pytest.fixture
def make_app():
    apps = []

    def _make(**kwargs):
        defaults = {
            "board_size": 16,
            "max_iter": 100,
            "rand_rate": 0,
            "fps": 1,
            "frequency": 4,
        }
        defaults.update(kwargs)
        app = PygameApp(**defaults)
        apps.append(app)
        return app

    yield _make
    pygame.quit()


def test_opens_paused_on_setup(make_app):
    app = make_app()
    assert app._config_editable
    assert app.paused is True
    assert app._simulation_started is False
    assert app.generation == 0
    assert app.status == "Configure settings, then Start"


def test_start_locks_config_and_stays_paused(make_app):
    app = make_app()
    app.start_simulation()
    assert app._simulation_started is True
    assert app._config_editable is False
    assert app.paused is True
    assert app.generation == 0
    assert app.status == "Paused"
    app.start_simulation()
    assert app.generation == 0


def test_enter_starts_from_setup(make_app):
    app = make_app()
    pygame.event.clear()
    _post_key(pygame.K_RETURN)
    app._handle_events()
    assert app._simulation_started is True
    assert app.paused is True


def test_start_button_click_starts(make_app):
    app = make_app()
    pygame.event.clear()
    _click(app._start_button_rect.center)
    app._handle_events()
    assert app._simulation_started is True


def test_space_toggles_pause_after_start(make_app):
    app = make_app()
    app.start_simulation()
    pygame.event.clear()
    _post_key(pygame.K_SPACE)
    app._handle_events()
    assert app.paused is False
    assert app.status == "Running"
    _post_key(pygame.K_SPACE)
    app._handle_events()
    assert app.paused is True
    assert app.status == "Paused"


def test_r_returns_to_setup(make_app):
    app = make_app()
    app.start_simulation()
    pygame.event.clear()
    _post_key(pygame.K_r)
    app._handle_events()
    assert app._simulation_started is False
    assert app._config_editable
    assert app.generation == 0
    assert app.status == "Configure settings, then Start"


def test_escape_and_q_quit(make_app):
    app = make_app()
    pygame.event.clear()
    _post_key(pygame.K_ESCAPE)
    app._handle_events()
    assert app._running is False
    app = make_app()
    pygame.event.clear()
    _post_key(pygame.K_q)
    app._handle_events()
    assert app._running is False


def test_left_at_generation_zero_stays_at_start(make_app):
    app = make_app()
    app.start_simulation()
    app._step_back()
    assert app.generation == 0
    assert app.status == "Paused (at start)"


def test_empty_board_stops_as_repeating_pattern(make_app):
    app = make_app(rand_rate=0)
    app.start_simulation()
    app._step_forward()
    assert app._finished is True
    assert app.status == "Stopped (repeating pattern)"
    assert app.generation == 0


def test_unpause_advances_generation_for_blinker(make_app):
    app = make_app(rand_rate=0)
    app.start_simulation()
    app.game.board.add_object(set(BLINKER_V))
    app.paused = False
    app._simulate_steps()
    assert app.generation == 1
    assert app._finished is False


def test_step_forward_hits_max_iterations(make_app):
    app = make_app(max_iter=2, rand_rate=0, board_size=32)
    app.start_simulation()
    app.game.board.add_object(set(GLIDER))
    app._step_forward()
    assert app.generation == 1
    assert app._finished is False
    app._step_forward()
    assert app.generation == 2
    assert app._finished is True
    assert app.status == "Stopped (max iterations)"


def test_simulate_steps_does_not_mark_finished_until_next_frame(make_app):
    # Unlike _step_forward, _simulate_steps increments generation then
    # waits until the next call to apply the max-iter stop.
    app = make_app(max_iter=2, rand_rate=0, board_size=32)
    app.start_simulation()
    app.game.board.add_object(set(GLIDER))
    app.paused = False
    app._simulate_steps()
    app._simulate_steps()
    assert app.generation == 2
    assert app._finished is False
    app._simulate_steps()
    assert app._finished is True
    assert app.status == "Stopped (max iterations)"


def test_topology_cycle_rebuilds_sphere_board(make_app):
    app = make_app(topology=Topology.BOUNDED)
    assert app._is_sphere is False
    app._inc_topology()
    assert app.topology == Topology.TOROIDAL
    app._inc_topology()
    assert app.topology == Topology.SPHERE
    assert app._is_sphere is True
    assert isinstance(app.game.board, GeodesicBoard)
    assert app.game.board.cell_count == 162
    neighborhood = app.neighborhood
    app._inc_neighborhood()
    app._dec_neighborhood()
    assert app.neighborhood == neighborhood


def test_config_clicks_ignored_after_start(make_app):
    app = make_app()
    size_before = app.board_size
    app.start_simulation()
    pygame.event.clear()
    size_row = next(row for row in app._config_buttons if row["key"] == "board_size")
    _click(size_row["plus"].center)
    app._handle_events()
    assert app.board_size == size_before
    assert app._simulation_started is True


def test_draw_does_not_raise_for_grid_and_sphere(make_app):
    app = make_app()
    app._draw()
    app.start_simulation()
    app._draw()
    sphere = make_app(topology=Topology.SPHERE)
    sphere._draw()
    sphere.start_simulation()
    sphere._draw()
    assert sphere.sphere_renderer.zoom == 1.0
