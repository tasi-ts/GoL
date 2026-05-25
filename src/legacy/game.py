import sys
import copy
import matplotlib.pyplot as plt

from board import Board
from rules import Rules

MAX_DETECTED_PERIOD = 6

class GameOfLife:

    def __init__(self, init_board, rule_set, max_iter, rand_rate=0.5) -> None:
        self.board = init_board
        self.rule_set = rule_set
        self.max_iter = max_iter
        self.rand_rate = rand_rate
        self.sequence = []

    def check_area(self, array, x, y):
        summa = 0
        dead_cells = set()
        self.rule_set.calc_neighbors(x, y)
        for neighbor in self.rule_set.neighbors:
            x, y = neighbor
            if array[x][y] == 1:
                summa += 1
            elif array[x][y] == 0:
                dead_cells.add((x,y))
        return summa, dead_cells

    def advance_board(self):
        old_board = copy.deepcopy(self.board)
        for elem in old_board.cells:
            x, y = elem
            summa, dead_cells = self.check_area(old_board.array, x, y)
            if summa < 2 and old_board.array[x][y] == 1:
                self.board.array[x][y] = 0
                self.board.cells.remove(elem)
            if summa > 3 and old_board.array[x][y] == 1:
                self.board.array[x][y] = 0
                self.board.cells.remove(elem)
            for cell in dead_cells:
                dx, dy = cell
                summa, _ = self.check_area(old_board.array, dx, dy)
                if summa == 3 and old_board.array[dx][dy] == 0:
                    self.board.array[dx][dy] = 1
                    self.board.cells.add(cell)
        self.sequence.append(old_board)
        self.board.calc_area()

    def _boards_equal(self, board_a, board_b):
        return (
            board_a.cells == board_b.cells
            and board_a.array == board_b.array
        )

    def check_if_changed(self):
        for period in range(1, MAX_DETECTED_PERIOD + 1):
            if len(self.sequence) >= period:
                if self._boards_equal(self.board, self.sequence[-period]):
                    return False
        return True

    def run_simulation(self):
        if self.rand_rate:
            self.board.add_random_coords(rate=self.rand_rate)
        self.board.print_board()
        # self.board.print_cells()
        self.board.print_area()
        # self.board.display_board()
        for i in range(self.max_iter):
            self.advance_board()
            print("- Generation {0}. - maximum iteration: {1}".format(i, self.max_iter))
            # self.board.print_board()
            # self.board.print_cells()
            # self.board.print_area()
            if not self.check_if_changed():
                self.sequence.append(self.board)
                break
            # self.board.display_board()


def main():
    print(sys.executable)
    game = GameOfLife(init_board=Board(64), rule_set=Rules(8,64), max_iter=2500, rand_rate=0.50)
    game.run_simulation()
    # plt.imshow(game.sequence[0].convert_to_binary_image(), cmap='gray')
    # plt.show()
    fig, ax = plt.subplots()
    for i in range(len(game.sequence)):
        ax.cla()
        ax.imshow(game.sequence[i].convert_to_binary_image(), cmap='gray')
        ax.set_title("Generation {0}.".format(i))
        plt.pause(0.075)


if __name__ == "__main__":
    main()
