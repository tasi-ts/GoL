import pytest

from gol.board import FlatBoard
from gol.game import make_game
from gol.geodesic_board import GeodesicBoard
from gol.topology import Topology
from tests.helpers import BLOCK, GLIDER, seed_flat_game

pytestmark = pytest.mark.integration


def test_make_game_bounded():
    game = make_game(Topology.BOUNDED, board_size=12, neighborhood=4, max_iter=9)
    assert isinstance(game.board, FlatBoard)
    assert game.board.size == 12
    assert game.rule_set.neighborhood == 4
    assert game.rule_set.toroidal is False
    assert game.max_iter == 9


def test_make_game_toroidal():
    game = make_game(Topology.TOROIDAL, board_size=8, neighborhood=8)
    assert game.rule_set.toroidal is True
    assert game.board.rules is game.rule_set


def test_make_game_sphere():
    game = make_game(Topology.SPHERE, frequency=3, max_iter=15, rand_rate=0.1)
    assert isinstance(game.board, GeodesicBoard)
    assert game.rule_set is None
    assert game.board.cell_count == 92
    assert game.max_iter == 15
    assert game.rand_rate == 0.1


def test_run_simulation_stops_on_block(capsys):
    game = seed_flat_game(BLOCK, size=6, max_iter=20, rand_rate=0)
    game.run_simulation(verbose=True)
    captured = capsys.readouterr()
    assert "repeating pattern" in captured.out
    assert game.board.live_cells == BLOCK
    assert len(game.sequence) >= 1


def test_run_simulation_stops_at_max_iter_for_glider(capsys):
    game = seed_flat_game(GLIDER, size=32, max_iter=3, rand_rate=0)
    game.run_simulation(verbose=True)
    captured = capsys.readouterr()
    assert "max iteration 3" in captured.out
    assert len(game.board.live_cells) == 5


def test_run_simulation_verbose_false_is_silent(capsys):
    game = seed_flat_game(BLOCK, size=6, max_iter=5, rand_rate=0)
    game.run_simulation(verbose=False)
    assert capsys.readouterr().out == ""


def test_make_game_then_random_initialize_then_step():
    game = make_game(
        Topology.BOUNDED,
        board_size=16,
        neighborhood=8,
        max_iter=10,
        rand_rate=0.4,
    )
    game.initialize_board()
    assert game.board.area == 102
    changed = game.step()
    assert isinstance(changed, bool)
    game.board.calc_area()
    assert game.board.area == len(game.board.live_cells)


def test_sphere_random_run_stays_within_mesh():
    game = make_game(Topology.SPHERE, frequency=2, max_iter=8, rand_rate=0.5)
    game.initialize_board()
    assert game.board.area == 21
    for _ in range(8):
        if not game.step():
            break
        assert game.board.live_cells <= set(range(game.board.cell_count))
