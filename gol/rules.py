from .types import Coord

CORE_OFFSETS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
DIAG_OFFSETS = [(-1, -1), (1, -1), (-1, 1), (1, 1)]


class Rules:

    def __init__(self, neighborhood: int, size: int, toroidal: bool = False) -> None:
        self.neighborhood = neighborhood
        self.size = size
        self.toroidal = toroidal

    @property
    def neighborhood(self) -> int:
        return self._neighborhood

    @neighborhood.setter
    def neighborhood(self, value: int) -> None:
        if not (value == 4 or value == 8):
            raise ValueError("--- Neighborhood must be 4 or 8! ---")
        self._neighborhood = value

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, value: int) -> None:
        if not value > 2:
            raise ValueError("--- Size must be greater than 2! ---")
        self._size = value

    @property
    def toroidal(self) -> bool:
        return self._toroidal

    @toroidal.setter
    def toroidal(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise ValueError("--- Toroidal must be True or False! ---")
        self._toroidal = value

    def neighbors(self, x: int, y: int) -> set[Coord]:
        """Return neighbor coordinates. Does not mutate instance state."""
        result: set[Coord] = set()
        if not (0 <= x < self.size and 0 <= y < self.size):
            return result
        offsets = CORE_OFFSETS
        if self.neighborhood == 8:
            offsets = CORE_OFFSETS + DIAG_OFFSETS
        for dx, dy in offsets:
            nx, ny = x + dx, y + dy
            if self.toroidal:
                nx %= self.size
                ny %= self.size
            elif not (0 <= nx < self.size and 0 <= ny < self.size):
                continue
            result.add((nx, ny))
        return result
