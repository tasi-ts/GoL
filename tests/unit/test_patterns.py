import pytest

from gol.cli import parse_args
from gol.game import apply_pattern, make_game
from gol.patterns import CLI_PATTERNS, get_pattern
from gol.topology import Topology
from tests.helpers import BLINKER_H, BLOCK, seed_flat_game

pytestmark = pytest.mark.unit


def test_cli_pattern_names_match_catalog():
    assert tuple(CLI_PATTERNS) == (
        "block",
        "blinker",
        "toad",
        "glider",
        "beehive",
    )


def test_helpers_reexport_the_same_objects():
    from gol import patterns
    from tests import helpers

    assert helpers.BLOCK is patterns.BLOCK
    assert helpers.GLIDER is patterns.GLIDER
    assert helpers.BLINKER_V is patterns.BLINKER_V


def test_block_is_still_life():
    game = seed_flat_game(CLI_PATTERNS["block"], size=8)
    assert game.step() is False
    assert game.board.live_cells == CLI_PATTERNS["block"]


def test_beehive_is_still_life():
    game = seed_flat_game(CLI_PATTERNS["beehive"], size=8)
    assert game.step() is False
    assert game.board.live_cells == CLI_PATTERNS["beehive"]


def test_blinker_period_two():
    game = seed_flat_game(CLI_PATTERNS["blinker"], size=8)
    assert game.step() is True
    assert game.board.live_cells == BLINKER_H
    assert game.step() is False
    assert game.board.live_cells == CLI_PATTERNS["blinker"]


def test_toad_period_two():
    pattern = CLI_PATTERNS["toad"]
    game = seed_flat_game(pattern, size=8)
    assert game.step() is True
    assert game.board.live_cells != pattern
    assert game.step() is False
    assert game.board.live_cells == pattern


def test_glider_translates():
    pattern = CLI_PATTERNS["glider"]
    game = seed_flat_game(pattern, size=16)
    for _ in range(4):
        assert game.step() is True
    shifted = {(row + 1, col + 1) for row, col in pattern}
    assert game.board.live_cells == shifted


def test_apply_pattern_after_empty_initialize():
    game = make_game(Topology.BOUNDED, board_size=8, rand_rate=0)
    game.initialize_board()
    assert game.board.live_cells == set()
    apply_pattern(game, BLOCK)
    assert game.board.live_cells == BLOCK
    assert game.step_back() is False
    assert game.board.live_cells == BLOCK


def test_get_pattern_unknown():
    with pytest.raises(ValueError, match="unknown pattern"):
        get_pattern("rpentomino")


def test_parse_args_defaults():
    args = parse_args([])
    assert args.pattern is None
    assert args.seed is None
    assert args.topology == "bounded"
    assert args.size == 64
    assert args.frequency == 8


def test_parse_args_pattern_glider():
    args = parse_args(["--pattern", "glider", "--topology", "toroidal", "--size", "32"])
    assert args.pattern == "glider"
    assert args.topology == "toroidal"
    assert args.size == 32


def test_parse_args_rejects_pattern_on_sphere():
    with pytest.raises(SystemExit) as exc:
        parse_args(["--pattern", "glider", "--topology", "sphere"])
    assert exc.value.code == 2


def test_parse_args_help_exits_zero(capsys):
    with pytest.raises(SystemExit) as exc:
        parse_args(["--help"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "--pattern" in out
    assert "glider" in out


def test_main_help_does_not_call_launch(monkeypatch):
    from gol import cli

    monkeypatch.setattr(cli, "launch", lambda args: pytest.fail("launch called"))
    with pytest.raises(SystemExit) as exc:
        cli.main(["--help"])
    assert exc.value.code == 0
