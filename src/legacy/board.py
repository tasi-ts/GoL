import matplotlib.pyplot as plt
import random

class Board:

    def __init__(self, size) -> None:
        self.size = size
        self.array = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.cells = set()
        self.area = 0

    def print_cells(self):
        print(self.cells, end="\n\n")

    def print_area(self):
        print("Area: {}".format(self.area), end="\n\n")

    def print_board(self):
        for i in range(self.size):
            for j in range(self.size):
                print("{0}".format(self.array[i][j]), end=" ")
            print()
        print()

    def convert_to_binary_image(self):
        return [[self.array[j][i] * 255 for i in range(self.size)] for j in range(self.size)]

    def display_board(self):
        img = self.convert_to_binary_image()
        plt.imshow(img, cmap='gray')
        plt.show()

    def add_object(self, coord_set):
        self.cells = self.cells.union(coord_set)
        for elem in coord_set:
            x, y = elem
            self.array[x][y] = 1
        self.calc_area()

    def add_random_coords(self, rate=None):
        if rate is None:
            num = int(self.size*self.size*0.5)
        else:
            num = int(self.size*self.size*rate)
            # print("Num: {}".format(num), end="\n\n")
        cnt = 0
        while cnt < num:
            x = random.randrange(self.size)
            y = random.randrange(self.size)
            if not ((x,y) in self.cells):
                self.cells.add((x,y))
                self.array[x][y] = 1
                cnt += 1
                # print("cnt: {}".format(cnt))
        self.calc_area()
        # self.print_area()

    def calc_area(self):
        area_array = int(sum([sum(row) for row in self.array]))
        area_cells = len(self.cells)
        if not area_array == area_cells:
            raise Exception("--- Area is inconsistent! ---")
        self.area = area_cells
