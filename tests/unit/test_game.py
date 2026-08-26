import pytest

from gol.board import FlatBoard
from gol.game import BIRTH, MAX_DETECTED_PERIOD, SURVIVE, GameOfLife
from gol.geodesic_board import GeodesicBoard
from gol.rules import Rules
from tests.helpers import (
    BEEHIVE,
    BLINKER_H,
    BLINKER_V,
    BLOCK,
    GLIDER,
    TOAD_A,
    seed_flat_game,
    seed_sphere_game,
)

pytestmark = pytest.mark.unit


def test_empty_board_is_still_life_on_first_step():
    game = seed_flat_game(cells=(), size=5)
    assert game.step() is False
    assert game.board.live_cells == set()


def test_block_stops_as_period_one():
    game = seed_flat_game(BLOCK, size=6)
    assert game.step() is False
    assert game.board.live_cells == BLOCK


def test_beehive_is_still_life():
    game = seed_flat_game(BEEHIVE, size=8)
    assert game.step() is False
    assert game.board.live_cells == BEEHIVE


def test_blinker_oscillates_period_two_under_moore():
    game = seed_flat_game(BLINKER_V, size=8, neighborhood=8)
    assert game.step() is True
    assert game.board.live_cells == BLINKER_H
    assert game.step() is False
    assert game.board.live_cells == BLINKER_V


def test_toad_oscillates_period_two():
    game = seed_flat_game(TOAD_A, size=8, neighborhood=8)
    assert game.step() is True
    second = frozenset(game.board.live_cells)
    assert second != TOAD_A
    assert game.step() is False
    assert game.board.live_cells == TOAD_A


def test_blinker_does_not_oscillate_under_von_neumann():
    game = seed_flat_game(BLINKER_V, size=8, neighborhood=4)
    assert game.step() is True
    assert game.board.live_cells == {(3, 3)}
    assert game.step() is True
    assert game.board.live_cells == set()
    assert game.step() is False


def test_glider_translates_on_bounded_board():
    game = seed_flat_game(GLIDER, size=16, neighborhood=8)
    assert game.step() is True
    after_one = frozenset(game.board.live_cells)
    assert after_one != GLIDER
    assert len(after_one) == 5
    game.step()
    game.step()
    game.step()
    shifted = {(row + 1, col + 1) for row, col in GLIDER}
    assert game.board.live_cells == shifted


def test_glider_wraps_on_toroidal_board():
    size = 10
    cells = {(row + 6, col + 6) for row, col in GLIDER}
    game = seed_flat_game(cells, size=size, neighborhood=8, toroidal=True)
    for _ in range(4):
        assert game.step() is True
    wrapped = {((row + 1) % size, (col + 1) % size) for row, col in cells}
    assert game.board.live_cells == wrapped


def test_step_back_at_start_returns_false():
    game = seed_flat_game(BLOCK, size=6)
    assert game.step_back() is False


def test_step_back_restores_previous_generation():
    game = seed_flat_game(BLINKER_V, size=8)
    game.step()
    assert game.board.live_cells == BLINKER_H
    assert game.step_back() is True
    assert game.board.live_cells == BLINKER_V
    assert game.step_back() is False


def test_step_back_after_still_life_stop_stays_at_start():
    # After a still-life stop, history's last snapshot equals the current
    # board, so step_back() drains history and reports already-at-start.
    game = seed_flat_game(BLOCK, size=6)
    assert game.step() is False
    assert game.step_back() is False
    assert game.board.live_cells == BLOCK


def test_rand_rate_zero_skips_random_fill():
    rules = Rules(8, 6)
    board = FlatBoard(6, rules=rules)
    game = GameOfLife(board, rule_set=rules, max_iter=5, rand_rate=0)
    game.initialize_board()
    assert game.board.live_cells == set()
    assert game.board.area == 0


def test_rand_rate_float_zero_skips_random_fill():
    rules = Rules(8, 6)
    board = FlatBoard(6, rules=rules)
    game = GameOfLife(board, rule_set=rules, max_iter=5, rand_rate=0.0)
    game.initialize_board()
    assert game.board.live_cells == set()


def test_rand_rate_truthy_seeds_random_cells():
    rules = Rules(8, 10)
    board = FlatBoard(10, rules=rules)
    game = GameOfLife(board, rule_set=rules, max_iter=5, rand_rate=0.3, seed=0)
    game.initialize_board()
    assert game.board.area == 30


def test_birth_and_survive_are_b3_s23():
    assert BIRTH == frozenset({3})
    assert SURVIVE == frozenset({2, 3})


def test_max_detected_period_is_six():
    assert MAX_DETECTED_PERIOD == 6


def test_period_window_is_capped_history_is_not():
    game = seed_flat_game(GLIDER, size=32, max_iter=20)
    for _ in range(10):
        assert game.step() is True
    assert len(game.sequence) == 10
    assert len(game._period_window) == MAX_DETECTED_PERIOD


def test_sphere_still_life_single_isolated_cell_dies():
    game = seed_sphere_game(cells={0}, frequency=2)
    assert game.step() is True
    assert game.board.live_cells == set()
    assert game.step() is False


def test_sphere_board_type():
    game = seed_sphere_game(frequency=2)
    assert isinstance(game.board, GeodesicBoard)
    assert game.rule_set is None
