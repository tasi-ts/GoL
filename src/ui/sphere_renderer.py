import math

import numpy as np
import pygame


class SphereRenderer:
    """Draw a GeodesicBoard as a depth-sorted 3D mesh in grid_rect."""

    def __init__(
        self,
        color_alive=(0, 200, 120),
        color_dead=(30, 30, 36),
        color_edge=(42, 42, 50),
    ):
        self.color_alive = color_alive
        self.color_dead = color_dead
        self.color_edge = color_edge
        self.yaw = 0.6
        self.pitch = 0.35
        self.zoom = 1.0
        self._dragging = False
        self._last_mouse = None

    def _rotation_matrix(self):
        cy, sy = math.cos(self.yaw), math.sin(self.yaw)
        cp, sp = math.cos(self.pitch), math.sin(self.pitch)
        ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]], dtype=np.float64)
        rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]], dtype=np.float64)
        return rx @ ry

    def _project(self, points, rot, rect):
        rotated = points @ rot.T
        depth = rotated[:, 2]
        scale = min(rect.width, rect.height) * 0.42 * self.zoom
        cx = rect.centerx
        cy = rect.centery
        sx = cx + rotated[:, 0] * scale
        sy = cy - rotated[:, 1] * scale
        return np.column_stack([sx, sy]), depth

    def handle_event(self, event, grid_rect):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if grid_rect.collidepoint(event.pos):
                self._dragging = True
                self._last_mouse = event.pos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._dragging = False
            self._last_mouse = None
        elif event.type == pygame.MOUSEMOTION and self._dragging:
            if self._last_mouse is not None:
                dx = event.pos[0] - self._last_mouse[0]
                dy = event.pos[1] - self._last_mouse[1]
                self.yaw += dx * 0.01
                self.pitch += dy * 0.01
                self.pitch = max(-1.4, min(1.4, self.pitch))
                self._last_mouse = event.pos
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if grid_rect.collidepoint(event.pos):
                if event.button == 4:
                    self.zoom = min(3.0, self.zoom * 1.08)
                elif event.button == 5:
                    self.zoom = max(0.4, self.zoom / 1.08)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFTBRACKET:
                self.zoom = max(0.4, self.zoom / 1.08)
            elif event.key == pygame.K_RIGHTBRACKET:
                self.zoom = min(3.0, self.zoom * 1.08)

    def draw(self, surface, board, grid_rect):
        mesh = board.mesh
        rot = self._rotation_matrix()
        pygame.draw.rect(surface, self.color_dead, grid_rect)

        draw_items = []
        for cell_id in range(mesh.cell_count):
            polygon = mesh.cell_polygons[cell_id]
            if not polygon:
                continue
            pts = np.array(polygon, dtype=np.float64)
            screen_pts, depth = self._project(pts, rot, grid_rect)
            avg_depth = float(np.mean(depth))
            color = self.color_alive if board.is_alive(cell_id) else self.color_dead
            draw_items.append((avg_depth, screen_pts, color))

        draw_items.sort(key=lambda item: item[0])

        for _, screen_pts, color in draw_items:
            points = [(int(x), int(y)) for x, y in screen_pts]
            if len(points) >= 3:
                pygame.draw.polygon(surface, color, points)
                pygame.draw.polygon(surface, self.color_edge, points, 1)

        pygame.draw.rect(surface, (0, 200, 120), grid_rect, 2)
