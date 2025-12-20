from __future__ import annotations

import random
import pygame as pg
from typing import override

from src.scenes.scene import Scene
from src.sprites import Sprite
from src.interface.components import Button
from src.core.services import scene_manager, sound_manager
from src.utils import GameSettings
from src.sprites import BackgroundSprite, Sprite


class CatchPokemonScene(Scene):
    """
    Simple scene shown after colliding with a bush.

    - Same background as battle scene.
    - Two buttons: 'Catch Pokemon' and 'Run'.
    - On catch: add a new monster to the Bag used in GameScene, then go back.
    """

    def __init__(self) -> None:
        super().__init__()

        # same background style as battle_scene
        self.background = BackgroundSprite("backgrounds/background2.png")
        #self.pokemon = Sprite("menu_sprites/menusprite4.png", (300,300))


        # pixel font (fallback to default if file missing)
        try:
            self.font = pg.font.Font("assets/fonts/Minecraft.ttf", 24)
        except FileNotFoundError:
            self.font = pg.font.Font(None, 24)

       
        self.monster_data = None
        self.pokemon = None


        # ----  ----
        BTN_SIZE = 100
        SPACING = 100

        cx = GameSettings.SCREEN_WIDTH // 2
        y = GameSettings.SCREEN_HEIGHT - 120


        self.catch_btn_rect = pg.Rect(
        cx - BTN_SIZE - SPACING // 2,
        y,
        BTN_SIZE,
        BTN_SIZE
        )

        self.run_btn_rect = pg.Rect(
        cx + SPACING // 2,
        y,
        BTN_SIZE,
        BTN_SIZE
        )


        self.catch_button = Button(
            "UI/raw/UI_Flat_Button02a_4.png", "UI/raw/UI_Flat_Button02a_1.png",
            self.catch_btn_rect.x, self.catch_btn_rect.y,
            BTN_SIZE, BTN_SIZE,
            self._on_catch,
        )
        
        self.run_button = Button(
            "UI/button_x.png", "UI/button_x_hover.png",
            self.run_btn_rect.x, self.run_btn_rect.y,
            BTN_SIZE, BTN_SIZE,
            self._on_run
        )

    def _on_run(self) -> None:
        self._clear_pending_encounter()
        self._reset_encounter_view()
        scene_manager.change_scene("game", transition=True, duration=0.25)


    # ------------------------------------------------------------------ helpers --

    def _get_encounter_monster(self) -> dict:
        scenes = getattr(scene_manager, "_scenes", {})
        game_scene = scenes.get("game")

        if game_scene and hasattr(game_scene, "game_manager"):
            gm = game_scene.game_manager
            enc = getattr(gm, "pending_encounter", None)
            if isinstance(enc, dict):
                return enc

        # fallback always returns something valid
        lvl = random.randint(3, 7)
        max_hp = 60 + 5 * lvl
        return {
            "name": "Bushmon",
            "element": "grass",
            "level": lvl,
            "hp": max_hp,
            "max_hp": max_hp,
            "sprite_path": "menu_sprites/menusprite1.png",
        }


    def _clear_pending_encounter(self) -> None:
        scenes = getattr(scene_manager, "_scenes", {})
        game_scene = scenes.get("game")
        if game_scene and hasattr(game_scene, "game_manager"):
            game_scene.game_manager.pending_encounter = None


    def _add_monster_to_bag(self) -> None:
        """
        Append the new monster into the SAME Bag instance that GameScene uses.

        We grab the 'game' scene out of SceneManager's scene dictionary and
        touch its game_manager.bag directly, so the Backpack overlay updates
        immediately.
        """
        scenes = getattr(scene_manager, "_scenes", {})
        game_scene = scenes.get("game")

        if game_scene is None or not hasattr(game_scene, "game_manager"):
            # fail-safe: nothing to do
            return

        bag = game_scene.game_manager.bag

        # Bag may expose different APIs; try them in order.
        if hasattr(bag, "add_monster"):
            bag.add_monster(self.monster_data)
        elif hasattr(bag, "monsters"):
            bag.monsters.append(self.monster_data)
        elif hasattr(bag, "_monsters_data"):
            bag._monsters_data.append(self.monster_data)
        
        #self.game_manager.save("saves/game0.json")

    # ---------------------------------------------------------- button callbacks --

    def _on_catch(self) -> None:
        self._add_monster_to_bag()
        self._clear_pending_encounter()
        self._reset_encounter_view()
        try:
            sound_manager.play_sound("SFX/CATCH_SUCCESS.ogg", 0.7)
        except Exception:
            pass
        scene_manager.change_scene("game", transition=True, duration=0.25)



    # --------------------------------------------------------------- Scene API ----

    @override
    def enter(self) -> None:
    # every time we enter this scene, pull the pending encounter again
        self.monster_data = self._get_encounter_monster()
        self.pokemon = Sprite(self.monster_data["sprite_path"], (200, 200))
        self.pokemon.rect.midbottom = (
            GameSettings.SCREEN_WIDTH // 2,
            GameSettings.SCREEN_HEIGHT // 2 + 80
        )
    def _reset_encounter_view(self) -> None:
        self.monster_data = None
        self.pokemon = None


    @override
    def update(self, dt: float) -> None:
        self.catch_button.update(dt)
        self.run_button.update(dt)

    @override
    def draw(self, screen: pg.Surface) -> None:
        # background
        self.background.draw(screen)
        if self.monster_data is None or self.pokemon is None:
            self.catch_button.draw(screen)
            self.run_button.draw(screen)
            return
        self.pokemon.draw(screen)

        # title & message
        title = self.font.render("Wild Pokemon found!", True, (0, 0, 0))
        msg   = self.font.render("Catch this Pokemon?", True, (0, 0, 0))
        screen.blit(
            title,
            (GameSettings.SCREEN_WIDTH // 2 - title.get_width() // 2, 40),
        )
        screen.blit(
            msg,
            (GameSettings.SCREEN_WIDTH // 2 - msg.get_width() // 2, 100),
        )
        name = self.monster_data["name"]
        lvl = self.monster_data["level"]
        info = self.font.render(f"{name}  Lv{lvl}", True, (0, 0, 0))
        screen.blit(info, (GameSettings.SCREEN_WIDTH//2 - info.get_width()//2, 140))

        # draw buttons
        self.catch_button.draw(screen)
        self.run_button.draw(screen)

        # button labels (centered using our own rects)
        catch_label = self.font.render("Catch Pokemon", True, (0, 0, 0))
        run_label   = self.font.render("Run", True, (0, 0, 0))

        

        screen.blit(
            catch_label,
            (
                self.catch_btn_rect.centerx - catch_label.get_width() // 2,
                self.catch_btn_rect.top - 28   # text ABOVE button
        )
        )

        screen.blit(
            run_label,
            (
                self.run_btn_rect.centerx - run_label.get_width() // 2,
                self.run_btn_rect.top - 28
            )
        )

