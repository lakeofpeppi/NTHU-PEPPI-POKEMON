
from __future__ import annotations
import pygame as pg

from src.core.services import input_manager
from src.sprites import Sprite
from .component import UIComponent


class Slider(UIComponent):
    """
    Horizontal slider in [0,1].

    Uses:
      - bar sprite:  UI/raw/UI_Flat_Bar08a.png
      - knob sprite: UI/raw/UI_Flat_ToggleOff02a.png
    """

    def __init__(self, x: int, y: int, width: int, initial_value: float = 1.0):
        # bar height fixed by asset, but we pass (width, 12)
        self.bar_sprite = Sprite("UI/raw/UI_Flat_Bar08a.png", (width, 12 * 3))
        self.knob_sprite = Sprite("UI/raw/UI_Flat_ToggleOff02a.png", (16, 16))

        self.bar_rect = self.bar_sprite.image.get_rect()
        # x,y is center of bar
        self.bar_rect.center = (x, y)

        self.knob_rect = self.knob_sprite.image.get_rect()
        self.dragging = False

        self.value = max(0.0, min(1.0, float(initial_value)))



        self.on_change = None  # type: ignore[assignment]

        self._update_knob_from_value()

    # --- internal helpers ---
    def _update_knob_from_value(self) -> None:
        # Allowed range for knob center, so it never goes outside the bar
        center_min = self.bar_rect.left + self.knob_rect.width // 2
        center_max = self.bar_rect.right - self.knob_rect.width // 2

        cx = center_min + self.value * (center_max - center_min)
        self.knob_rect.centerx = int(cx)
        self.knob_rect.centery = self.bar_rect.centery


    def _update_value_from_mouse(self) -> None:
        mx, _ = input_manager.mouse_pos

        # Same range as in _update_knob_from_value
        center_min = self.bar_rect.left + self.knob_rect.width // 2
        center_max = self.bar_rect.right - self.knob_rect.width // 2
        if center_max == center_min:
            return

        # Clamp mouse within the valid range
        mx = max(center_min, min(mx, center_max))

        # Convert position -> value in [0,1]
        t = (mx - center_min) / (center_max - center_min)
        #self.value = max(0.1, min(0.9, t))
        self.value = max(0.1, min(0.9, t))
        self._update_knob_from_value()
        if self.on_change is not None:
            self.on_change(self.value)


    # --- UIComponent API ---
    def update(self, dt: float) -> None:
        mouse_pos = input_manager.mouse_pos

        # start drag
        if input_manager.mouse_pressed(1) and self.knob_rect.collidepoint(mouse_pos):
            self.dragging = True

        # stop drag
        if not input_manager.mouse_down(1):
            self.dragging = False

        # drag
        if self.dragging:
            self._update_value_from_mouse()

    def draw(self, screen: pg.Surface) -> None:
        screen.blit(self.bar_sprite.image, self.bar_rect)
        screen.blit(self.knob_sprite.image, self.knob_rect)

    
