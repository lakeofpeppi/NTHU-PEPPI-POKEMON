import pygame as pg

from src.scenes.scene import Scene
from src.core import GameManager
from src.core.services import scene_manager
from src.utils import GameSettings
from src.sprites import Sprite
from src.interface.components import Button

from typing import override


class CatchPokemonScene(Scene):
    """
    Simple scene: same background style as battle,
    shows a 'Catch Pokemon' button and 'Run' button.
    On catch, adds a monster to the bag and returns to game.
    """

    def __init__(self) -> None:
        super().__init__()

        # TODO: replace BATTLE_BACKGROUND.png with your real battle bg path
        self.background = Sprite("backgrounds/background2.png",
                                 (GameSettings.SCREEN_WIDTH,
                                  GameSettings.SCREEN_HEIGHT))

        # Press Start 2P font you installed earlier
        # Put PressStart2P.ttf in assets/fonts/PressStart2P.ttf
        try:
            self.font = pg.font.Font("fonts/PressStart2P.ttf", 24)
        except FileNotFoundError:
            self.font = pg.font.Font(None, 24)   # fallback

        # Buttons at bottom center
        btn_w, btn_h = 220, 60
        center_x = GameSettings.SCREEN_WIDTH // 2
        bottom_y = GameSettings.SCREEN_HEIGHT - 100

        # TODO: replace BUTTON_NORMAL.png / BUTTON_HOVER.png with your own
        self.catch_button = Button(
            "UI/raw/UI_Flat_Button02a_3.png", "UI/raw/UI_Flat_Button02a_1.png",
            center_x - btn_w - 20, bottom_y, btn_w, btn_h,
            self._on_catch
        )
        self.run_button = Button(
            "UI/raw/UI_Flat_Button02a_3.png", "UI/raw/UI_Flat_Button02a_1.png",
            center_x + 20, bottom_y, btn_w, btn_h,
            self._on_run
        )

        # hard-coded monster info (you can change later)
        self.mon_name = "Bushmon"
        self.mon_level = 5
        self.mon_hp = 50
        self.mon_max_hp = 50
       
        self.mon_sprite_path = "menu_sprites/menusprite10.png"

    # ------------- callbacks -------------

    def _on_catch(self) -> None:
        """
        Add new monster to bag & save to file,
        then return to game scene.
        """
        gm = GameManager.load("saves/game0.json")
        if gm is None:
            # if something goes wrong, just go back
            scene_manager.change_scene("game")
            return

        new_mon = {
            "name": self.mon_name,
            "hp": self.mon_hp,
            "max_hp": self.mon_max_hp,
            "level": self.mon_level,
            "sprite_path": self.mon_sprite_path,
        }

        # Bag is a Bag() instance; we use its method
        gm.bag.add_monster(new_mon)
        gm.save("saves/game0.json")

        scene_manager.change_scene("game")

    def _on_run(self) -> None:
        """Just go back without catching."""
        scene_manager.change_scene("game")

    # ------------- Scene API -------------

    @override
    def update(self, dt: float) -> None:
        self.catch_button.update(dt)
        self.run_button.update(dt)

    @override
    def draw(self, screen: pg.Surface) -> None:
        self.background.draw(screen)

        # text: "A wild Bushmon appeared! Catch?"
        title = f"A wild {self.mon_name} appeared!"
        subtitle = "Catch this Pokémon?"
        title_surf = self.font.render(title, True, (0, 0, 0))
        subtitle_surf = self.font.render(subtitle, True, (0, 0, 0))

        screen.blit(
            title_surf,
            (GameSettings.SCREEN_WIDTH // 2 - title_surf.get_width() // 2,
             40),
        )
        screen.blit(
            subtitle_surf,
            (GameSettings.SCREEN_WIDTH // 2 - subtitle_surf.get_width() // 2,
             80),
        )

        # draw buttons with labels
        self.catch_button.draw(screen)
        self.run_button.draw(screen)

        catch_label = self.font.render("Catch Pokémon", True, (0, 0, 0))
        run_label = self.font.render("Run", True, (0, 0, 0))

        screen.blit(
            catch_label,
            (self.catch_button.rect.centerx - catch_label.get_width() // 2,
             self.catch_button.rect.centery - catch_label.get_height() // 2),
        )
        screen.blit(
            run_label,
            (self.run_button.rect.centerx - run_label.get_width() // 2,
             self.run_button.rect.centery - run_label.get_height() // 2),
        )
