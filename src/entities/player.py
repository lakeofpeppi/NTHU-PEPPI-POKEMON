from __future__ import annotations
import pygame as pg
from .entity import Entity
from src.core.services import input_manager
from src.utils import Position, PositionCamera, GameSettings, Logger
from src.core import GameManager
import math
from typing import override

class Player(Entity):
    speed: float = 4.0 * GameSettings.TILE_SIZE
    game_manager: GameManager

    def __init__(self, x: float, y: float, game_manager: GameManager) -> None:
        super().__init__(x, y, game_manager)
        self.facing_dir = "down"
        self.moving = False


    @override
    def update(self, dt: float) -> None:
        dis = Position(0, 0)
        '''
        [TODO HACKATHON 2]
        Calculate the distance change, and then normalize the distance
        
        [TODO HACKATHON 4]
        Check if there is collision, if so try to make the movement smooth
        Hint #1 : use entity.py _snap_to_grid function or create a similar function
        Hint #2 : Beware of glitchy teleportation, you must do
                    1. Update X
                    2. If collide, snap to grid
                    3. Update Y
                    4. If collide, snap to grid
                  instead of update both x, y, then snap to grid
        
        if input_manager.key_down(pg.K_LEFT) or input_manager.key_down(pg.K_a):
            dis.x -= ...
        if input_manager.key_down(pg.K_RIGHT) or input_manager.key_down(pg.K_d):
            dis.x += ...
        if input_manager.key_down(pg.K_UP) or input_manager.key_down(pg.K_w):
            dis.y -= ...
        if input_manager.key_down(pg.K_DOWN) or input_manager.key_down(pg.K_s):
            dis.y += ...
        
        self.position = ...
        '''
        dis = Position(0.0, 0.0)
        if input_manager.key_down(pg.K_LEFT) or input_manager.key_down(pg.K_a):
            dis.x -= 1
        if input_manager.key_down(pg.K_RIGHT) or input_manager.key_down(pg.K_d):
            dis.x += 1
        if input_manager.key_down(pg.K_UP) or input_manager.key_down(pg.K_w):
            dis.y -= 1
        if input_manager.key_down(pg.K_DOWN) or input_manager.key_down(pg.K_s):
            dis.y += 1

        length = math.hypot(dis.x, dis.y)
        moving = length > 0.0
        if moving:
            dis.x /= length
            dis.y /= length

        else:
            pass
        # applying speed and delta-time HADEH
            self.position.x += dis.x * self.speed * dt
            self.position.y += dis.y * self.speed * dt

        if moving:
    # pick a facing direction (dominant axis) for diagonals
            if abs(dis.x) > abs(dis.y):
                if dis.x > 0:
                    self.animation.switch("right")
                else:
                    self.animation.switch("left")
            else:
                if dis.y > 0:
                    self.animation.switch("down")   # front
                else:
                    self.animation.switch("up")     # back
        else:
            # optional: stop walking animation when idle
            self.animation.accumulator = 0.0

        ts = GameSettings.TILE_SIZE
        speed = self.speed * dt
        
        def collider_rect_at(x: float, y: float) -> pg.Rect:
            return pg.Rect(int(x), int(y), ts, ts)
        
        def collides_any(rect: pg.Rect) -> bool:
        # Map collision
            if self.game_manager.current_map.check_collision(rect):
                return True
        # Enemy collision
            for enemy in self.game_manager.current_enemy_trainers:
            # Try common collider attribute names, fall back to tile-sized rect
                er = getattr(enemy, "collider", None)
                if er is None:
                    er = getattr(enemy, "rect", None)
                if er is None:
                    ex = getattr(enemy, "position", Position(0, 0)).x
                    ey = getattr(enemy, "position", Position(0, 0)).y
                    er = pg.Rect(int(ex), int(ey), ts, ts)
                if rect.colliderect(er):
                    return True
            return False
        
        if length > 0 and dis.x != 0:
            new_x = self.position.x + dis.x * speed
            rect_x = collider_rect_at(new_x, self.position.y)
            if not collides_any(rect_x):
                self.position.x = new_x
        # else:
        #     self._snap_to_grid(axis="x", direction=dis.x)  # if you have it

    # Move Y
        if length > 0 and dis.y != 0:
            new_y = self.position.y + dis.y * speed
            rect_y = collider_rect_at(self.position.x, new_y)
            if not collides_any(rect_y):
                self.position.y = new_y
        # else:
        #     self._snap_to_grid(axis="y", direction=dis.y)  # if you have it


        # Check teleportation
        tp = self.game_manager.current_map.check_teleport(self.position)
        if tp:
            dest = tp.destination
            self.game_manager.switch_map(dest)

        if tp and tp.destination not in self.game_manager.maps:
            Logger.warning(f"Teleport destination '{tp.destination}' not loaded")

                
       # super().update(dt)
        self.animation.update_pos(self.position)
        if moving:
            self.animation.update(dt)

        

        



    @override
    def draw(self, screen: pg.Surface, camera: PositionCamera) -> None:
        super().draw(screen, camera)
        
    @override
    def to_dict(self) -> dict[str, object]:
        return super().to_dict()
    
    @classmethod
    @override
    def from_dict(cls, data: dict[str, object], game_manager: GameManager) -> Player:
        return cls(data["x"] * GameSettings.TILE_SIZE, data["y"] * GameSettings.TILE_SIZE, game_manager)

