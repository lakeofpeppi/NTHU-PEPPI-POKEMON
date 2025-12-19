from __future__ import annotations
import pygame as pg
from typing import override

from .entity import Entity
from src.core import GameManager
from src.core.services import input_manager
from src.sprites import Animation
from src.utils import GameSettings, Direction, Position, PositionCamera


class ShopNPC(Entity):
    near: bool
    facing: Direction

    @override
    def __init__(self, x: float, y: float, game_manager: GameManager, facing: Direction = Direction.DOWN) -> None:
        # call base Entity to set position/game_manager
        super().__init__(x, y, game_manager)

        # OVERRIDE animation to your shop girl spritesheet
        self.animation = Animation(
            "character/ow3.png",                 # <-- put ow3.png into assets/images/character/ow3.png
            ["down", "left", "right", "up"],     # must match your sheet row order
            4,                                   # columns (frames per row)
            (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE),
            loop=0.8                             # speed (smaller = faster)
        )

        self.facing = facing
        self._set_direction(facing)

        self.near = False
        self.emote_font = pg.font.Font("assets/fonts/Minecraft.ttf", 12)
        # --- badge style (white circle + black border + bold text) ---
        self.badge_size = int(GameSettings.TILE_SIZE * 0.55)   # tweak: 0.5~0.7 looks good
        self.badge_text = "^_^"  # or "^__^" if you want
        self.badge_surf = self._make_badge_surface(self.badge_text, self.badge_size)


        # how close to interact (pixels)
        self.detect_radius = GameSettings.TILE_SIZE * 2

        self.animation.update_pos(self.position)

    def _set_direction(self, direction: Direction) -> None:
        self.direction = direction
        if direction == Direction.RIGHT:
            self.animation.switch("right")
        elif direction == Direction.LEFT:
            self.animation.switch("left")
        elif direction == Direction.DOWN:
            self.animation.switch("down")
        else:
            self.animation.switch("up")

    def _is_player_near(self) -> bool:
        p = self.game_manager.player
        if p is None:
            return False
        dx = p.position.x - self.position.x
        dy = p.position.y - self.position.y
        return (dx * dx + dy * dy) <= (self.detect_radius * self.detect_radius)

    @override
    def update(self, dt: float) -> None:
        # stay still, just animate idle
        self.near = self._is_player_near()

        self.animation.update_pos(self.position)
        self.animation.update(dt)

    def _make_badge_surface(self, text: str, size: int) -> pg.Surface:
        surf = pg.Surface((size, size), pg.SRCALPHA)

        # circle background + outline
        r = size // 2
        center = (r, r)
        pg.draw.circle(surf, (255, 255, 255), center, r)       # fill
        pg.draw.circle(surf, (0, 0, 0), center, r, 3)          # outline thickness

        # bold-ish text: render twice with slight offset (simple fake bold)
        t = self.emote_font.render(text, True, (0, 0, 0))
        tx = center[0] - t.get_width() // 2
        ty = center[1] - t.get_height() // 2

        surf.blit(t, (tx, ty))
        surf.blit(t, (tx + 1, ty))  # makes it a bit bolder

        return surf

    @override
    def draw(self, screen: pg.Surface, camera: PositionCamera) -> None:
        # draw sprite
        super().draw(screen, camera)

        # draw "^__^" when near
        if self.near:
            #text = self.emote_font.render("^__^", True, (255, 255, 255))
            sx = int(self.position.x - camera.x + (GameSettings.TILE_SIZE - self.badge_size) // 2)
            sy = int(self.position.y - camera.y - self.badge_size - 8)

            screen.blit(self.badge_surf, (sx, sy))

    def interact_pressed(self) -> bool:
        # only triggers once per key press
        return self.near and input_manager.key_pressed(pg.K_SPACE)
