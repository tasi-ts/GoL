CORE_OFFSETS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
DIAG_OFFSETS = [(-1, -1), (1, -1), (-1, 1), (1, 1)]


class Rules:

    def __init__(self, neighborhood, size, toroidal=False) -> None:
        self.neighborhood = neighborhood
        self.size = size
        self.toroidal = toroidal

    @property
    def neighborhood(self):
        return self._neighborhood

    @property
    def size(self):
        return self._size

    @property
    def toroidal(self):
        return self._toroidal

    @neighborhood.setter
    def neighborhood(self, value):
        if not (value == 4 or value == 8):
            raise ValueError("--- Neighborhood must be 4 or 8! ---")
        self._neighborhood = value

    @size.setter
    def size(self, value):
        if not value > 2:
            raise ValueError("--- Size must be greater than 2! ---")
        self._size = value

    @toroidal.setter
    def toroidal(self, value):
        if not isinstance(value, bool):
            raise ValueError("--- Toroidal must be True or False! ---")
        self._toroidal = value

    def neighbors(self, x, y):
        """Return neighbor coordinates. Does not mutate instance state."""
        result = set()
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
