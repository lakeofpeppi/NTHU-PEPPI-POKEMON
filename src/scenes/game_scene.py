import pygame as pg
import threading
import time
import random

from src.scenes.scene import Scene
from src.core import GameManager, OnlineManager
from src.utils import Logger, PositionCamera, GameSettings, Position
from src.core.services import scene_manager, sound_manager
from src.interface.components import Button, Slider, Checkbox
from src.sprites import Sprite
from typing import override

class GameScene(Scene):
    game_manager: GameManager
    online_manager: OnlineManager | None
    sprite_online: Sprite
    back_button: Button
    overlay_button: Button       # open overlay
    overlay_back_button: Button  # close overlay
    overlay_open: bool
    backpack_button: Button
    backpack_back_button: Button
    backpack_open: bool
    bag_font: pg.font.Font

    # NEW: bush / catching UI
    near_bush: bool
    catch_button: Button
    catch_font: pg.font.Font

    def __init__(self):
        super().__init__()
        self.in_bush = False 
        # Game Manager
        manager = GameManager.load("saves/game0.json")
        if manager is None:
            Logger.error("Failed to load game manager")
            exit(1)
        self.game_manager = manager
        
        # Online Manager
        if GameSettings.IS_ONLINE:
            self.online_manager = OnlineManager()
        else:
            self.online_manager = None
        self.sprite_online = Sprite("ingame_ui/options1.png", (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE))

        # Back to menu
        self.back_button = Button(
            "UI/button_back.png", "UI/button_back_hover.png",
            20, 20, 80, 80,
            lambda: scene_manager.change_scene("menu")
        )

        # overlay button (settings)
        btn_w, btn_h = 80, 80
        open_x = GameSettings.SCREEN_WIDTH - btn_w - 20
        open_y = 20
        self.overlay_button = Button(
            "UI/button_setting.png", "UI/button_setting_hover.png",
            open_x, open_y, btn_w, btn_h,
            self._open_overlay
        )

        cx = GameSettings.SCREEN_WIDTH // 2
        cy = GameSettings.SCREEN_HEIGHT // 2

        # Slider for master volume (0..1 internally)
        self.overlay_volume_slider = Slider(
            cx, cy - 40,          # center position inside overlay
            200,                  # width
            sound_manager.get_bgm_volume()
        )
        # When slider moves, change bgm volume immediately
        self.overlay_volume_slider.on_change = lambda v: sound_manager.set_bgm_volume(v)

        # Save & Load buttons inside the overlay
        btn_w, btn_h = 80, 80
        center_x = GameSettings.SCREEN_WIDTH  // 2
        bottom_y = GameSettings.SCREEN_HEIGHT // 2 + 120
        self.overlay_save_button = Button(
            "UI/button_save.png", "UI/button_save_hover.png",
            center_x - btn_w - 10,  # left of center
            bottom_y,
            btn_w, btn_h,
            self._save_game
        )

        self.overlay_back_button = Button(
            "UI/button_back.png", "UI/button_back_hover.png",
            center_x + 10,          # right of center
            bottom_y,
            btn_w, btn_h,
            self._close_overlay
        )
        self.overlay_font = pg.font.Font("assets/fonts/Minecraft.ttf", 28)

        # (optional) load button – if you want it visible, draw it in draw()
        self.overlay_load_button = Button(
            "UI/button_load.png", "UI/button_load_hover.png",
            cx + 20, cy + 30, btn_w, btn_h,
            self._load_game
        )

        self.overlay_open = False

        # BACKPACK UI (same as before)
        self.backpack_open = False
        bag_btn_x = open_x
        bag_btn_y = open_y + btn_h + 10
        self.backpack_button = Button(
            "UI/button_backpack.png", "UI/button_backpack_hover.png",
            bag_btn_x, bag_btn_y, btn_w, btn_h,
            self._open_backpack
        )

        bag_close_x = GameSettings.SCREEN_WIDTH // 2 - btn_w // 2
        bag_close_y = GameSettings.SCREEN_HEIGHT // 2 + 120
        self.backpack_back_button = Button(
            "UI/button_back.png", "UI/button_back_hover.png",
            bag_close_x, bag_close_y, btn_w, btn_h,
            self._close_backpack
        )

        self.bag_font = pg.font.Font("assets/fonts/Minecraft.ttf", 18)

        # ----------- NEW: bush / catch button -----------
        self.near_bush = False
        self.catch_font = pg.font.Font("assets/fonts/Minecraft.ttf", 20)

        catch_w, catch_h = 220, 50
        catch_x = GameSettings.SCREEN_WIDTH // 2 - catch_w // 2
        catch_y = GameSettings.SCREEN_HEIGHT - catch_h - 30

        # Use temporary button sprites – replace with your own PNG later:
        self.catch_button = Button(
            "UI/raw/UI_Flat_ToggleOff01a.png",        # TODO: replace with your asset
            "UI/raw/UI_Flat_ToggleOff02a.png",  # TODO: replace with your asset
            catch_x, catch_y, catch_w, catch_h,
            self._catch_pokemon
        )
        self.catch_button.rect = pg.Rect(
            catch_x, catch_y, catch_w, catch_h
            )
        # ------------------------------------------------

    # ------------ open/close overlays -----------------

    def _open_overlay(self) -> None:
        self.overlay_open = True

    def _close_overlay(self) -> None:
        self.overlay_open = False

    def _open_backpack(self) -> None:
        self.backpack_open = True

    def _close_backpack(self) -> None:
        self.backpack_open = False

    # --------------------------------------------------
        
    @override
    def enter(self) -> None:
        sound_manager.play_bgm("RBY 103 Pallet Town.ogg")
        if self.online_manager:
            self.online_manager.enter()
        
    @override
    def exit(self) -> None:
        if self.online_manager:
            self.online_manager.exit()
        
    @override
    def update(self, dt: float):
        # when overlay is open, only overlay UI is updated
        if self.overlay_open:
            self.overlay_back_button.update(dt)
            self.overlay_volume_slider.update(dt)
            self.overlay_save_button.update(dt)
            self.overlay_load_button.update(dt)
            return

        if self.backpack_open:
            self.backpack_back_button.update(dt)
            return
        
        if self.game_manager.player:
            px = self.game_manager.player.position.x
            py = self.game_manager.player.position.y

            '''
            on_bush = self.game_manager.current_map.is_bush_tile(px, py)

            # player just stepped ON a bush tile this frame
            if on_bush and not self.in_bush:
                self.in_bush = True
                scene_manager.change_scene("catchpokemon")
                return  # stop updating after scene switch

            # player is NOT on a bush tile anymore
            elif not on_bush:
                self.in_bush = False
                '''
            if self.game_manager.current_map.consume_bush_at_pixel(px, py):
                from src.core.services import scene_manager
                scene_manager.change_scene("catchpokemon")
                return


        # Check if there is assigned next scene
        self.game_manager.try_switch_map()
        
        # Update player and other data
        if self.game_manager.player:
            self.game_manager.player.update(dt)
        for enemy in self.game_manager.current_enemy_trainers:
            enemy.update(dt)
            
        # Update others
        self.game_manager.bag.update(dt)
        
                # --- Bush interaction: stand on bush + press E to catch ---
        if self.game_manager.player is not None:
            ts = GameSettings.TILE_SIZE
            px = int(self.game_manager.player.position.x // ts)
            py = int(self.game_manager.player.position.y // ts)

            from src.core.services import input_manager  # at top of file you probably already import this elsewhere
            if self.game_manager.current_map.is_bush_tile(px, py):
                    #and input_manager.key_pressed(pg.K_e)):
                # go to catch-pokemon scene
                from src.core.services import scene_manager
                scene_manager.change_scene("catchpokemon")
                return

        self.back_button.update(dt)
        self.overlay_button.update(dt)
        self.backpack_button.update(dt)

        # ----------- NEW: detect bushes & update catch button -----------
        self.near_bush = False
        if self.game_manager.player:
            ts = GameSettings.TILE_SIZE
            px = int(self.game_manager.player.position.x // ts)
            py = int(self.game_manager.player.position.y // ts)

            if self.game_manager.current_map.is_bush_tile(px, py):
                self.near_bush = True

        if self.near_bush:
            self.catch_button.update(dt)
        # ----------------------------------------------------------------

    @override
    def draw(self, screen: pg.Surface):        
        if self.game_manager.player:
            # camera follow player
            player = self.game_manager.player
            map_surface = self.game_manager.current_map._surface  # pixel size of the whole map
            map_w, map_h = map_surface.get_size()
            cam_x = int(player.position.x - GameSettings.SCREEN_WIDTH  // 2)
            cam_y = int(player.position.y - GameSettings.SCREEN_HEIGHT // 2)
            cam_x = max(0, min(cam_x, max(0, map_w - GameSettings.SCREEN_WIDTH)))
            cam_y = max(0, min(cam_y, max(0, map_h - GameSettings.SCREEN_HEIGHT)))

            camera = PositionCamera(cam_x, cam_y)
            self.game_manager.current_map.draw(screen, camera)
            self.game_manager.player.draw(screen, camera)
        else:
            camera = PositionCamera(0, 0)
            self.game_manager.current_map.draw(screen, camera)

        for enemy in self.game_manager.current_enemy_trainers:
            enemy.draw(screen, camera)

        self.game_manager.bag.draw(screen)
        
        if self.online_manager and self.game_manager.player:
            list_online = self.online_manager.get_list_players()
            for player in list_online:
                if player["map"] == self.game_manager.current_map.path_name:
                    cam = self.game_manager.player.camera
                    pos = cam.transform_position_as_position(Position(player["x"], player["y"]))
                    self.sprite_online.update_pos(pos)
                    self.sprite_online.draw(screen)

        self.back_button.draw(screen)
        self.overlay_button.draw(screen)
        self.backpack_button.draw(screen)

        # ----------- NEW: draw Catch button when near bush -----------
        if (not self.overlay_open) and (not self.backpack_open) and self.near_bush:
            self.catch_button.draw(screen)
            # draw text on top using Minecraft font
            label = self.catch_font.render("Catch Pokemon", True, (0, 0, 0))
            lx = self.catch_button.rect.x + (self.catch_button.rect.width - label.get_width()) // 2
            ly = self.catch_button.rect.y + (self.catch_button.rect.height - label.get_height()) // 2
            screen.blit(label, (lx, ly))
        # --------------------------------------------------------------

        # SETTINGS overlay
        if self.overlay_open:
            # Darken background
            overlay_surface = pg.Surface(
                (GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT),
                pg.SRCALPHA
            )
            overlay_surface.fill((0, 0, 0, 150))
            screen.blit(overlay_surface, (0, 0))

            rect_width = GameSettings.SCREEN_WIDTH // 2
            rect_height = GameSettings.SCREEN_HEIGHT // 2
            rect_x = GameSettings.SCREEN_WIDTH // 4
            rect_y = GameSettings.SCREEN_HEIGHT // 4
            overlay_rect = pg.Rect(rect_x, rect_y, rect_width, rect_height)
            pg.draw.rect(screen, (200, 200, 200), overlay_rect)
            pg.draw.rect(screen, (0, 0, 0), overlay_rect, 3)

            title = self.overlay_font.render("Settings", True, (0, 0, 0))
            screen.blit(
                title,
                (rect_x + (rect_width - title.get_width()) // 2,
                 rect_y + 10)
            )

            # Volume label + percentage (0..100)
            vol_percent = int(self.overlay_volume_slider.value * 100)
            vol_text = self.overlay_font.render(
                f"Volume: {vol_percent}", True, (0, 0, 0)
            )
            screen.blit(
                vol_text,
                (rect_x + 30, rect_y + 60)
            )

            # Draw slider itself
            self.overlay_volume_slider.draw(screen)

            # Draw Save button
            self.overlay_save_button.draw(screen)

            # Back button to close overlay
            self.overlay_back_button.draw(screen)

        if self.backpack_open:
            self._draw_backpack_overlay(screen)

    # ---------------- BACKPACK overlay (unchanged) ------------------

    def _draw_backpack_overlay(self, screen: pg.Surface) -> None:
        # darken background
        dim = pg.Surface(
            (GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT),
            pg.SRCALPHA
        )
        dim.fill((0, 0, 0, 150))
        screen.blit(dim, (0, 0))

        # center panel
        panel_w, panel_h = 640, 360
        panel_x = (GameSettings.SCREEN_WIDTH  - panel_w) // 2
        panel_y = (GameSettings.SCREEN_HEIGHT - panel_h) // 2
        panel_rect = pg.Rect(panel_x, panel_y, panel_w, panel_h)

        pg.draw.rect(screen, (240, 240, 240), panel_rect)
        pg.draw.rect(screen, (0, 0, 0), panel_rect, 3)

        # title
        title_surf = self.bag_font.render("Backpack", True, (0, 0, 0))
        screen.blit(
            title_surf,
            (panel_x + (panel_w - title_surf.get_width()) // 2, panel_y + 10)
        )

        # column labels
        monsters_label = self.bag_font.render("Monsters", True, (0, 0, 0))
        items_label    = self.bag_font.render("Items", True, (0, 0, 0))

        monsters_x = panel_x + 20
        items_x    = panel_x + panel_w // 2 + 20
        header_y   = panel_y + 50

        screen.blit(monsters_label, (monsters_x, header_y))
        screen.blit(items_label,    (items_x,    header_y))

        # ---- list monsters (uses data from save/load) ----
        y = header_y + 30
        for mon in self.game_manager.bag._monsters_data:
            line = f"{mon['name']} Lv{mon['level']} HP {mon['hp']}/{mon['max_hp']}"
            text_surf = self.bag_font.render(line, True, (0, 0, 0))
            screen.blit(text_surf, (monsters_x, y))
            y += 24

        # ---- list items ----
        y = header_y + 30
        for item in self.game_manager.bag._items_data:
            line = f"{item['name']} x{item['count']}"
            text_surf = self.bag_font.render(line, True, (0, 0, 0))
            screen.blit(text_surf, (items_x, y))
            y += 24

        # back button inside overlay
        self.backpack_back_button.draw(screen)

    # ---------------- save / load helpers ------------------

    def _save_game(self) -> None:
        # write current game state to disk
        self.game_manager.save("saves/game0.json")

    def _load_game(self) -> None:
        # read game state back and replace manager
        new_manager = GameManager.load("saves/game0.json")
        if new_manager is not None:
            self.game_manager = new_manager

    # ---------------- NEW: catching logic ------------------

    def _catch_pokemon(self) -> None:
        """
        Called when the 'Catch Pokemon' button is clicked while standing on a bush.
        For now we just create a simple monster and insert it into the bag.
        You can replace the stats/sprite_path with your real monsters.
        """
        if not self.near_bush:
            return

        # simple fake monster – replace with your own design later
        new_mon = {
            "name": "Bushmon",
            "hp": 60,
            "max_hp": 60,
            "level": random.randint(3, 7),
            "sprite_path": "menu_sprites/menusprite1.png"
        }

        self.game_manager.bag._monsters_data.append(new_mon)
        Logger.info(f"Caught a wild {new_mon['name']}!")

        # optional SFX if you have one
        try:
            sound_manager.play_sound("SFX/POKEBALL_CAPTURE.wav", volume=0.7)
        except Exception:
            pass  # ignore if the sound file doesn't exist
