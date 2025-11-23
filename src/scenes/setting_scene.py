'''
[TODO HACKATHON 5]
Try to mimic the menu_scene.py or game_scene.py to create this new scene
'''
#brandnew settingsscene
import pygame as pg

from src.scenes.scene import Scene
from src.utils import GameSettings
from src.sprites import BackgroundSprite
from src.interface.components import Button, Checkbox, Slider
from src.core.services import scene_manager, sound_manager, input_manager
from typing import override


class SettingScene(Scene):
    def __init__(self):
        super().__init__()
        self.background = BackgroundSprite("backgrounds/background1.png")
        #self.font = pg.font.Font(None, 28)
        # center positions
        center_x = GameSettings.SCREEN_WIDTH // 2
        center_y = GameSettings.SCREEN_HEIGHT // 2

        # ------ back button 
        self.back_button = Button(
            "UI/button_back.png", "UI/button_back_hover.png",
            center_x - 200, center_y + 120, 100, 100,
            lambda: scene_manager.change_scene("menu")
        )

        box_size = 32

        #fonts
        self.font = pg.font.Font("assets/fonts/Minecraft.ttf", 24)


         # Checkboxes
        self.music_checkbox = Checkbox(center_x - 220, center_y - 55, box_size, True)
        self.sfx_checkbox   = Checkbox(center_x - 220, center_y - 15, box_size, True)


        # Sliders (use current volumes as default)
        self.music_slider = Slider(center_x + 40, center_y - 40,
                                   200, sound_manager.get_bgm_volume())
        self.sfx_slider   = Slider(center_x + 40, center_y,
                                   200, sound_manager.get_sfx_volume())

        # Connect callbacks
        self.music_checkbox.on_toggle = lambda checked: self._update_volumes()
        self.sfx_checkbox.on_toggle   = lambda checked: self._update_volumes()
        self.music_slider.on_change   = lambda v: self._update_volumes()
        self.sfx_slider.on_change     = lambda v: self._update_volumes()

        # initial sync
        self._update_volumes()


    #volume logic 
    def _update_volumes(self) -> None:
        # if checkbox OFF → volume 0, else → slider value
        music_vol = self.music_slider.value if self.music_checkbox.checked else 0.0
        sfx_vol   = self.sfx_slider.value if self.sfx_checkbox.checked else 0.0

        sound_manager.set_bgm_volume(music_vol)
        sound_manager.set_sfx_volume(sfx_vol)

    # -------- lifecycle -------- #

    @override
    def enter(self) -> None:
        # nothing special
        pass

    @override
    def exit(self) -> None:
        pass

    @override
    def update(self, dt: float) -> None:
        # buttons, checkboxes, sliders
        self.back_button.update(dt)
        self.music_checkbox.update(dt)
        self.sfx_checkbox.update(dt)
        self.music_slider.update(dt)
        self.sfx_slider.update(dt)

    @override
    def draw(self, screen: pg.Surface) -> None:
        self.background.draw(screen)
        self.music_checkbox.draw(screen)
        self.sfx_checkbox.draw(screen)
        self.music_slider.draw(screen)
        self.sfx_slider.draw(screen)
        self.back_button.draw(screen)
        # ----- Draw labels -----
        music_text = self.font.render("Music", True, (0, 0, 0))
        sfx_text   = self.font.render("SFX",   True, (0, 0, 0))

        # Position labels next to the checkboxes
        screen.blit(music_text,(self.music_checkbox.rect.right + 10, self.music_checkbox.rect.y + 5))
        screen.blit(sfx_text,(self.sfx_checkbox.rect.right + 10, self.sfx_checkbox.rect.y + 5))
