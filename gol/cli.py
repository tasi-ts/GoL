"""Console entry point. Parses flags before importing pygame."""

import argparse
from collections.abc import Sequence

from .patterns import CLI_PATTERNS, get_pattern
from .topology import Topology

PATTERN_CHOICES = tuple(CLI_PATTERNS)
TOPOLOGY_CHOICES = ("bounded", "toroidal", "sphere")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="gol",
        description=(
            "Conway's Game of Life with bounded, toroidal, and geodesic "
            "sphere topologies."
        ),
    )
    parser.add_argument(
        "--pattern",
        choices=PATTERN_CHOICES,
        help=(
            "Seed a named pattern on a flat board, skip random fill, and "
            "open already Started (paused; Space runs). Not valid with "
            "--topology sphere."
        ),
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="RNG seed for random fill (ignored when --pattern is set).",
    )
    parser.add_argument(
        "--topology",
        choices=TOPOLOGY_CHOICES,
        default="bounded",
        help="Board topology (default: bounded).",
    )
    parser.add_argument(
        "--size",
        type=int,
        default=64,
        help="Flat board size (default: 64, large enough not to clip a glider).",
    )
    parser.add_argument(
        "--frequency",
        type=int,
        default=8,
        help="Sphere subdivision frequency nu (default: 8).",
    )
    args = parser.parse_args(argv)
    if args.pattern is not None and args.topology == "sphere":
        parser.error(
            "--pattern is for flat topologies only (bounded or toroidal)"
        )
    if args.size <= 2:
        parser.error("--size must be greater than 2")
    if args.frequency < 1:
        parser.error("--frequency must be at least 1")
    return args


def launch(args: argparse.Namespace) -> None:
    from .game import apply_pattern
    from .ui.pygame_app import PygameApp, run_pygame_app

    topology = Topology(args.topology)
    if args.pattern is None:
        run_pygame_app(
            board_size=args.size,
            topology=topology,
            frequency=args.frequency,
            seed=args.seed,
        )
        return

    app = PygameApp(
        board_size=args.size,
        topology=topology,
        frequency=args.frequency,
        rand_rate=0,
        seed=args.seed,
    )
    app.start_simulation()
    apply_pattern(app.game, get_pattern(args.pattern))
    app.run()


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    launch(args)
