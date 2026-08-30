import pygame

from ..geodesic_mesh import GeodesicMesh
from .colors import (
    COLOR_ACCENT,
    COLOR_BUTTON,
    COLOR_BUTTON_BORDER,
    COLOR_BUTTON_DISABLED,
    COLOR_PANEL,
    COLOR_PANEL_BORDER,
    COLOR_START,
    COLOR_TEXT,
    COLOR_TEXT_DIM,
)
from .layout import (
    CONFIG_PAD,
    CONFIG_ROW_START_Y,
    ROW_HEIGHT,
    VALUE_BUTTON_GAP,
)


def board_size_label(app):
    if app._is_sphere:
        return "Frequency"
    return "Board size"


def board_size_value(app):
    if app._is_sphere:
        cells = GeodesicMesh.expected_cell_count(app.frequency)
        return "{0} ({1})".format(app.frequency, cells)
    return str(app.board_size)


def draw_button(app, rect, label, enabled=True, accent=False):
    fill = COLOR_START if accent else (
        COLOR_BUTTON if enabled else COLOR_BUTTON_DISABLED
    )
    pygame.draw.rect(app.screen, fill, rect)
    border = COLOR_ACCENT if accent else COLOR_BUTTON_BORDER
    pygame.draw.rect(app.screen, border, rect, 2)
    surf = app.font_small.render(label, True, COLOR_TEXT)
    tx = rect.x + (rect.width - surf.get_width()) // 2
    ty = rect.y + (rect.height - surf.get_height()) // 2
    app.screen.blit(surf, (tx, ty))


def draw_config_panel(app):
    x = app.panel_rect.x + CONFIG_PAD
    y = 24
    title = app.font_title.render("Game of Life", True, COLOR_ACCENT)
    app.screen.blit(title, (x, y))
    y += 32

    hint = app.font_small.render(
        "Settings (before Start only)", True, COLOR_TEXT_DIM
    )
    app.screen.blit(hint, (x, y))
    y = CONFIG_ROW_START_Y

    labels = {
        "board_size": board_size_label(app),
        "neighborhood": "Neighborhood",
        "topology": "Topology",
        "max_iter": "Max generations",
        "rand_rate": "Random rate",
    }
    values = {
        "board_size": board_size_value(app),
        "neighborhood": str(app.neighborhood),
        "topology": app.topology.label(),
        "max_iter": str(app.max_iter),
        "rand_rate": "{0:.0%}".format(app.rand_rate),
    }

    for row in app._config_buttons:
        key = row["key"]
        row_y = row["minus"].y
        label_color = COLOR_TEXT_DIM if (
            key == "neighborhood" and app._is_sphere
        ) else COLOR_TEXT
        label_surf = app.font.render(labels[key], True, label_color)
        app.screen.blit(label_surf, (row["label_x"], row_y + 5))
        val_color = COLOR_TEXT_DIM if (
            key == "neighborhood" and app._is_sphere
        ) else COLOR_ACCENT
        val_surf = app.font.render(values[key], True, val_color)
        val_x = row["minus"].x - VALUE_BUTTON_GAP - val_surf.get_width()
        app.screen.blit(val_surf, (val_x, row_y + 5))
        neigh_enabled = app._config_editable and not (
            key == "neighborhood" and app._is_sphere
        )
        draw_button(
            app, row["minus"], "-", enabled=neigh_enabled
        )
        draw_button(
            app, row["plus"], "+", enabled=neigh_enabled
        )
        y = row_y + ROW_HEIGHT

    if app._start_button_rect:
        draw_button(
            app,
            app._start_button_rect,
            "Start",
            enabled=app._config_editable,
            accent=True,
        )

    y = app._start_button_rect.bottom + 24
    hints = [
        "Enter  also starts",
        "R      new setup",
        "Esc    quit",
    ]
    if app._is_sphere:
        hints.insert(1, "Drag   rotate sphere")
        hints.insert(2, "[ ]    zoom")
    for line in hints:
        surf = app.font_small.render(line, True, COLOR_TEXT_DIM)
        app.screen.blit(surf, (x, y))
        y += surf.get_height() + 4


def draw_running_panel(app):
    x = app.panel_rect.x + 16
    y = 24
    if app._is_sphere:
        board_line = "Frequency: {0}  Cells: {1}".format(
            app.frequency,
            GeodesicMesh.expected_cell_count(app.frequency),
        )
    else:
        board_line = "Board: {0}  Neighbor: {1}".format(
            app.board_size, app.neighborhood
        )

    lines = [
        ("Conway's Game of Life", app.font_title, COLOR_ACCENT),
        ("", app.font, COLOR_TEXT),
        ("Generation: {0}".format(app.generation), app.font, COLOR_TEXT),
        ("Population: {0}".format(app.game.board.area), app.font, COLOR_TEXT),
        ("Status: {0}".format(app.status), app.font, COLOR_TEXT),
        (board_line, app.font, COLOR_TEXT_DIM),
        ("Topology: {0}".format(app.topology.label()), app.font, COLOR_TEXT_DIM),
        ("Max gen: {0}  Seed: {1:.0%}".format(
            app.max_iter, app.rand_rate
        ), app.font, COLOR_TEXT_DIM),
        ("Speed: {0} step(s)/frame".format(app.steps_per_frame), app.font, COLOR_TEXT_DIM),
        ("FPS cap: {0}".format(app.fps), app.font, COLOR_TEXT_DIM),
        ("", app.font, COLOR_TEXT),
        ("Space  pause / resume", app.font, COLOR_TEXT_DIM),
        ("R      back to setup", app.font, COLOR_TEXT_DIM),
        ("+/-    steps per frame", app.font, COLOR_TEXT_DIM),
        ("Up/Dn  FPS cap", app.font, COLOR_TEXT_DIM),
        ("Left   step back (1 frame)", app.font, COLOR_TEXT_DIM),
        ("Right  step forward (1 frame)", app.font, COLOR_TEXT_DIM),
        ("Esc    quit", app.font, COLOR_TEXT_DIM),
    ]
    if app._is_sphere:
        lines.insert(-1, ("Drag   rotate  [ ] zoom", app.font, COLOR_TEXT_DIM))
    for text, font, color in lines:
        if not text:
            y += 8
            continue
        surf = font.render(text, True, color)
        app.screen.blit(surf, (x, y))
        y += surf.get_height() + 6


def draw_panel(app):
    pygame.draw.rect(app.screen, COLOR_PANEL, app.panel_rect)
    pygame.draw.line(
        app.screen,
        COLOR_PANEL_BORDER,
        (app.panel_rect.x, 0),
        (app.panel_rect.x, app.window_height),
        2,
    )
    if app._config_editable:
        draw_config_panel(app)
    else:
        draw_running_panel(app)
