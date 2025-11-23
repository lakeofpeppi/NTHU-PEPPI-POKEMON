from __future__ import annotations
import pygame as pg

from .component import UIComponent
from src.core.services import input_manager
from typing import Callable


class Checkbox(UIComponent):
    def __init__(self, x: int, y: int, size: int = 24, checked: bool = False):
        # where it is and how big
        self.rect = pg.Rect(x, y, size, size)
        self.checked = checked

        # callback: set from outside, e.g.
        # checkbox.on_toggle = lambda checked: ...
        self.on_toggle: Callable[[bool], None] | None = None

    def update(self, dt: float) -> None:
        # Toggle when clicked
        if self.rect.collidepoint(input_manager.mouse_pos):
            if input_manager.mouse_pressed(1):  # left mouse
                self.checked = not self.checked

                # notify whoever is listening
                if self.on_toggle is not None:
                    self.on_toggle(self.checked)

    def draw(self, screen: pg.Surface) -> None:
        # outer box
        pg.draw.rect(screen, (255, 255, 255), self.rect)      # white fill
        pg.draw.rect(screen, (0, 0, 0), self.rect, 2)         # black border

        # filled inner square when checked
        if self.checked:
            inner = self.rect.inflate(-6, -6)
            pg.draw.rect(screen, (0, 0, 0), inner)
