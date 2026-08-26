"""Console entry point. Same defaults as ``python -m gol.game``."""

from .game import main as run_game


def main() -> None:
    run_game()
