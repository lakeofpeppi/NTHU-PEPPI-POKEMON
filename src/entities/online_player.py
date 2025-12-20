import pygame as pg
from src.sprites import Animation
from src.utils import Position, PositionCamera, GameSettings

class OnlinePlayer:
    def __init__(self, x: float, y: float):
        self.position = Position(x, y)
        self.facing_dir = "down"
        self.moving = False

        self.animation = Animation(
            "character/ow1.png",
            ["down", "left", "right", "up"],
            4,
            (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
        )
        self.animation.update_pos(self.position)

    def apply_state(self, x: float, y: float, direction: str, moving: bool) -> None:
        self.position.x = float(x)
        self.position.y = float(y)

        if direction not in ("up", "down", "left", "right"):
            direction = "down"
        self.facing_dir = direction
        self.moving = bool(moving)

        self.animation.switch(self.facing_dir)
        self.animation.update_pos(self.position)

        if not self.moving:
            self.animation.accumulator = 0.0

    def update(self, dt: float) -> None:
        # Only animate if moving
        if self.moving:
            self.animation.update(dt)

    def draw(self, screen: pg.Surface, camera: PositionCamera) -> None:
        self.animation.draw(screen, camera)
