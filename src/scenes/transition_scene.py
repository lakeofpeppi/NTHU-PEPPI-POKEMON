import pygame as pg
from src.scenes.scene import Scene


class TransitionScene(Scene):
    def __init__(self, from_scene: Scene, to_scene: Scene, duration: float = 0.25):
        super().__init__()
        self.from_scene = from_scene
        self.to_scene = to_scene

        self.half = max(0.05, float(duration))  # seconds per half
        self.t = 0.0
        self.alpha = 0

        self.swapped = False   # becomes True at midpoint
        self.done = False      # becomes True at end

    def update(self, dt: float) -> None:
        # update the visible scene
        if not self.swapped:
            self.from_scene.update(dt)
        else:
            self.to_scene.update(dt)

        self.t += dt

        if not self.swapped:
            p = min(1.0, self.t / self.half)      # 0..1
            self.alpha = int(255 * p)             # 0 -> 255
            if p >= 1.0:
                self.swapped = True               # midpoint reached
                self.t = 0.0
        else:
            p = min(1.0, self.t / self.half)
            self.alpha = int(255 * (1.0 - p))     # 255 -> 0
            if p >= 1.0:
                self.alpha = 0
                self.done = True

    def draw(self, screen: pg.Surface) -> None:
        # draw the visible scene
        if not self.swapped:
            self.from_scene.draw(screen)
        else:
            self.to_scene.draw(screen)

        # fade overlay
        overlay = pg.Surface(screen.get_size(), pg.SRCALPHA)
        overlay.fill((0, 0, 0, self.alpha))
        screen.blit(overlay, (0, 0))
