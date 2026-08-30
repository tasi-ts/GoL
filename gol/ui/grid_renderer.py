import pygame

from .colors import COLOR_ACCENT, COLOR_ALIVE, COLOR_DEAD, COLOR_GRID_LINE


def draw_grid(screen, board, grid_rect, cell_size):
    size = board.size
    cell = cell_size
    board_pixels = size * cell
    origin_x = grid_rect.x + (grid_rect.width - board_pixels) // 2
    origin_y = grid_rect.y + (grid_rect.height - board_pixels) // 2

    pygame.draw.rect(screen, COLOR_DEAD, grid_rect)
    for x in range(size):
        for y in range(size):
            if board.is_alive((x, y)):
                pygame.draw.rect(
                    screen,
                    COLOR_ALIVE,
                    pygame.Rect(
                        origin_x + y * cell,
                        origin_y + x * cell,
                        cell,
                        cell,
                    ),
                )

    if cell >= 6:
        for i in range(size + 1):
            x_pos = origin_x + i * cell
            y_pos = origin_y + i * cell
            pygame.draw.line(
                screen,
                COLOR_GRID_LINE,
                (origin_x, y_pos),
                (origin_x + size * cell, y_pos),
                1,
            )
            pygame.draw.line(
                screen,
                COLOR_GRID_LINE,
                (x_pos, origin_y),
                (x_pos, origin_y + size * cell),
                1,
            )

    pygame.draw.rect(screen, COLOR_ACCENT, grid_rect, 2)
