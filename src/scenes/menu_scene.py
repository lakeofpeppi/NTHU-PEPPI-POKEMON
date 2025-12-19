import pygame as pg
import math

from src.utils import GameSettings
from src.sprites import BackgroundSprite
from src.scenes.scene import Scene
from src.interface.components import Button
from src.core.services import scene_manager, sound_manager, input_manager
from typing import override

class MenuScene(Scene):
    # Background Image
    background: BackgroundSprite
    # Buttons
    play_button: Button
    title_pokemon_font: pg.font.Font
    title_wildwood_font: pg.font.Font

    pokemon_text: pg.Surface
    wildwood_text: pg.Surface

    pokemon_shadow: pg.Surface
    wildwood_shadow: pg.Surface

    pokemon_rect: pg.Rect
    wildwood_rect: pg.Rect
    
    def __init__(self):
        super().__init__()
        self.background = BackgroundSprite("backgrounds/background1.png")

        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT * 3 // 4
        self.play_button = Button(
            "UI/button_play.png", "UI/button_play_hover.png",
            px + 50, py, 100, 100,
            lambda: scene_manager.change_scene("game")
        )
         #addsettings button
        self.setting_button = Button(
            "UI/button_setting.png", "UI/button_setting_hover.png",
            px - 160, py, 100, 100,
            lambda: scene_manager.change_scene("setting")
        )
                # ===== TITLE FONTS =====
        self.title_pokemon_font = pg.font.Font(
            "assets/fonts/Rocabe.ttf", 130
        )
        self.title_wildwood_font = pg.font.Font(
            "assets/fonts/Corepix.ttf", 120
        )

        # ===== SHADOW TEXT =====
        self.pokemon_shadow = self.title_pokemon_font.render(
            "Pokemon", True, (0, 0, 0)
        )
        self.wildwood_shadow = self.title_wildwood_font.render(
            "Wildwood", True, (0, 0, 0)
        )

        # ===== MAIN TEXT =====
        self.pokemon_text = self.title_pokemon_font.render(
            "Pokemon", True, (255, 245, 220)
        )
        self.wildwood_text = self.title_wildwood_font.render(
            "Wildwood", True, (235, 215, 180)
        )

        center_x = GameSettings.SCREEN_WIDTH // 2

        self.pokemon_rect = self.pokemon_text.get_rect(
            center=(center_x, GameSettings.SCREEN_HEIGHT // 4)
        )
        self.wildwood_rect = self.wildwood_text.get_rect(
            center=(center_x, GameSettings.SCREEN_HEIGHT // 4 + 110)
        )
        self.title_t = 0.0

        self.pokemon_base_center = self.pokemon_rect.center
        self.wildwood_base_center = self.wildwood_rect.center


        
    @override
    def enter(self) -> None:
        sound_manager.play_bgm("oldvideogame.ogg")
        #pass


    @override
    def exit(self) -> None:
        pass

    @override
    def update(self, dt: float) -> None:
        self.title_t += dt
        if input_manager.key_pressed(pg.K_SPACE):
            scene_manager.change_scene("game")
            return
        self.play_button.update(dt)
        self.setting_button.update(dt) 



    @override
    def draw(self, screen: pg.Surface) -> None:
        self.background.draw(screen)

    # ===== WIGGLE =====
        amp = 6
        speed = 5.0
        dx = int(math.sin(self.title_t * speed) * amp)
        dy = int(math.cos(self.title_t * speed * 0.7) * amp)
        angle = math.sin(self.title_t * speed) * 2.0  # degrees

    # ===== ROTATE (make new surfaces) =====
        pokemon_rot = pg.transform.rotozoom(self.pokemon_text, angle, 1.0)
        pokemon_shadow_rot = pg.transform.rotozoom(self.pokemon_shadow, angle, 1.0)

        wildwood_rot = pg.transform.rotozoom(self.wildwood_text, -angle, 1.0)
        wildwood_shadow_rot = pg.transform.rotozoom(self.wildwood_shadow, -angle, 1.0)

        # ===== RECT from ROTATED surfaces (IMPORTANT) =====
        pokemon_rect = pokemon_rot.get_rect(center=(
            self.pokemon_base_center[0] + dx,
            self.pokemon_base_center[1] + dy
        ))
        wildwood_rect = wildwood_rot.get_rect(center=(
            self.wildwood_base_center[0] - dx,
            self.wildwood_base_center[1] + dy
        ))

    # ===== DRAW SHAxDOW FIRST =====
        screen.blit(pokemon_shadow_rot, pokemon_rect.move(6, 6))
        screen.blit(wildwood_shadow_rot, wildwood_rect.move(6, 6))

    # ===== DRAW TEXT =====
        screen.blit(pokemon_rot, pokemon_rect)
        screen.blit(wildwood_rot, wildwood_rect)

    # buttons
        self.play_button.draw(screen)
        self.setting_button.draw(screen)
