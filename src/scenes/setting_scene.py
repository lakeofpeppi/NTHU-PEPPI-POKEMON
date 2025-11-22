'''
[TODO HACKATHON 5]
Try to mimic the menu_scene.py or game_scene.py to create this new scene
'''
#brandnew settingsscene

# src/scenes/setting_scene.py
import pygame as pg
from typing import override

from src.scenes.scene import Scene
from src.sprites import BackgroundSprite
from src.interface.components import Button
from src.core.services import scene_manager, sound_manager, input_manager
from src.utils import GameSettings

class SettingScene(Scene):
    background: BackgroundSprite
    back_button: Button

    def __init__(self):
        super().__init__()
        # reuse the same background; change if you have a specific one
        self.background = BackgroundSprite("backgrounds/background1.png")

        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT * 3 // 4
        self.back_button = Button(
            "UI/button_back.png", "UI/button_back_hover.png",
            px - 50, py, 100, 100,
            lambda: scene_manager.change_scene("menu")
        )

    @override
    def enter(self) -> None:
        # optional: softer bgm, or reuse menu bgm
        sound_manager.play_bgm("RBY 101 Opening (Part 1).ogg")

    @override
    def update(self, dt: float) -> None:
        # quick keyboard escape
        if input_manager.key_pressed(pg.K_ESCAPE):
            scene_manager.change_scene("menu")
            return
        self.back_button.update(dt)

    @override
    def draw(self, screen: pg.Surface) -> None:
        self.background.draw(screen)
        self.back_button.draw(screen)
