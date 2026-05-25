class Rules:

    def __init__(self, neighborhood, size) -> None:
        self.neighborhood = neighborhood
        self.size = size
        self.neighbors = set()

    @property
    def neighborhood(self):
        return self._neighborhood

    @property
    def size(self):
        return self._size

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

    def calc_neighbors(self, x, y):
        self.neighbors = set()
        if not (x < self.size and y < self.size):
            return
        if self.neighborhood == 4 or self.neighborhood == 8:
            if x-1 >= 0 and y >= 0:
                self.neighbors.add((x-1,y))
            if x+1 < self.size and y >= 0:
                self.neighbors.add((x+1,y))
            if y-1 >= 0 and x >= 0:
                self.neighbors.add((x,y-1))
            if y+1 < self.size and x >= 0:
                self.neighbors.add((x,y+1))
        if self.neighborhood == 8:
            if x-1 >= 0 and y-1 >= 0:
                self.neighbors.add((x-1,y-1))
            if x+1 < self.size and y-1 >= 0:
                self.neighbors.add((x+1,y-1))
            if x-1 >= 0 and y+1 < self.size:
                self.neighbors.add((x-1,y+1))
            if x+1 < self.size and y+1 < self.size:
                self.neighbors.add((x+1,y+1))
