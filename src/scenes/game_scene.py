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

        

        # Backpack UI assets
        self.bag_title_font = pg.font.Font("assets/fonts/Minecraft.ttf", 22)
        self.bag_font = pg.font.Font("assets/fonts/Minecraft.ttf", 14)
        self.bag_small_font = pg.font.Font("assets/fonts/Minecraft.ttf", 10)

        # Panel geometry (reuse in update/draw)
        self.bag_panel_w, self.bag_panel_h = 760, 430
        self.bag_panel_x = (GameSettings.SCREEN_WIDTH  - self.bag_panel_w) // 2
        self.bag_panel_y = (GameSettings.SCREEN_HEIGHT - self.bag_panel_h) // 2

        # Load banner image for monster cards
        self.mon_banner_img = pg.image.load("assets/images/UI/raw/UI_Flat_Banner03a.png").convert_alpha()


        # Close button (top-right of panel)
        x_size = 48
        x_x = self.bag_panel_x + self.bag_panel_w - x_size - 14
        x_y = self.bag_panel_y + 14
        self.backpack_close_button = Button(
            "UI/button_x.png", "UI/button_x_hover.png",
            x_x, x_y, x_size, x_size,
            self._close_backpack
        )

        # Optional: map item names -> options icons (fallback to item['sprite_path'])
        self.item_icon_map = {
            "Potion": "ingame_ui/potion.png",
            "Coins": "ingame_ui/coin.png",
            "Pokeball": "ingame_ui/ball.png",
        }



        # ----------- NEW: bush / catch button -----------
        self.near_bush = False
        self.catch_font = pg.font.Font("assets/fonts/Minecraft.ttf", 20)

        catch_w, catch_h = 220, 50
        catch_x = GameSettings.SCREEN_WIDTH // 2 - catch_w // 2
        catch_y = GameSettings.SCREEN_HEIGHT - catch_h - 30

        
        self.catch_button = Button(
            "UI/raw/UI_Flat_ToggleOff01a.png",        # TODO: replace with your asset
            "UI/raw/UI_Flat_ToggleOff02a.png",  # TODO: replace with your asset
            catch_x, catch_y, catch_w, catch_h,
            self._catch_pokemon
        )
        self.catch_button.rect = pg.Rect(
            catch_x, catch_y, catch_w, catch_h
            )
        
                # ----------- Wild pokemon pool for bushes -----------
        # You can tweak these or load them from JSON later
        self.wild_pokemon_pool = [
            {"name": "Bushmon",      "base_hp": 60, "min_level": 2, "max_level": 5,  "sprite_path": "menu_sprites/menusprite1.png"},
            {"name": "Leaflynx",     "base_hp": 65, "min_level": 2, "max_level": 6,  "sprite_path": "menu_sprites/menusprite2.png"},
            {"name": "Verdpuma",     "base_hp": 75, "min_level": 3, "max_level": 7,  "sprite_path": "menu_sprites/menusprite3.png"},
            {"name": "Brownbit",     "base_hp": 55, "min_level": 1, "max_level": 4,  "sprite_path": "menu_sprites/menusprite4.png"},
            {"name": "Pebblip",      "base_hp": 50, "min_level": 1, "max_level": 4,  "sprite_path": "menu_sprites/menusprite5.png"},
            {"name": "Frostfox",     "base_hp": 70, "min_level": 3, "max_level": 7,  "sprite_path": "menu_sprites/menusprite6.png"},
            {"name": "Sparkpup",     "base_hp": 55, "min_level": 1, "max_level": 4,  "sprite_path": "menu_sprites/menusprite7.png"},
            {"name": "Rufffang",     "base_hp": 70, "min_level": 2, "max_level": 6,  "sprite_path": "menu_sprites/menusprite8.png"},
            {"name": "Blazewing",    "base_hp": 95, "min_level": 6, "max_level": 10, "sprite_path": "menu_sprites/menusprite9.png"},
            {"name": "Nightmew",     "base_hp": 60, "min_level": 3, "max_level": 7,  "sprite_path": "menu_sprites/menusprite10.png"},
            {"name": "Serpflare",    "base_hp": 75, "min_level": 4, "max_level": 8,  "sprite_path": "menu_sprites/menusprite11.png"},
            {"name": "Aquabit",      "base_hp": 60, "min_level": 2, "max_level": 6,  "sprite_path": "menu_sprites/menusprite12.png"},
            {"name": "Glidefin",     "base_hp": 65, "min_level": 2, "max_level": 6,  "sprite_path": "menu_sprites/menusprite13.png"},
            {"name": "Seascale",     "base_hp": 90, "min_level": 5, "max_level": 9,  "sprite_path": "menu_sprites/menusprite14.png"},
            {"name": "Sproutlet",    "base_hp": 45, "min_level": 1, "max_level": 3,  "sprite_path": "menu_sprites/menusprite15.png"},
            {"name": "Flutterleaf",  "base_hp": 70, "min_level": 3, "max_level": 7,  "sprite_path": "menu_sprites/menusprite16.png"},
        ]


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
        sound_manager.play_bgm("longvideogame.ogg")
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
            self.backpack_close_button.update(dt)
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
        if self.game_manager.player:
            px = self.game_manager.player.position.x
            py = self.game_manager.player.position.y

            if self.game_manager.current_map.consume_bush_at_pixel(px, py):
                template = random.choice(self.wild_pokemon_pool)
                level = random.randint(template["min_level"], template["max_level"])
                max_hp = template["base_hp"] + (level - 1) * 5

                self.game_manager.pending_encounter = {
                    "name": template["name"],
                    "hp": max_hp,
                    "max_hp": max_hp,
                    "level": level,
                    "sprite_path": template["sprite_path"],
                }

                scene_manager.change_scene("catchpokemon", transition=True, duration=0.5)
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
        dim = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pg.SRCALPHA)
        dim.fill((0, 0, 0, 140))
        screen.blit(dim, (0, 0))

        # panel
        x = self.bag_panel_x
        y = self.bag_panel_y
        w = self.bag_panel_w
        h = self.bag_panel_h
        panel = pg.Rect(x, y, w, h)

        # background like "bag"
        pg.draw.rect(screen, (235, 160, 70), panel, border_radius=10)
        pg.draw.rect(screen, (60, 35, 20), panel, 4, border_radius=10)

        # title
        title = self.bag_title_font.render("BAG", True, (40, 20, 10))
        screen.blit(title, (x + 18, y + 14))

        # close button (top-right)
        self.backpack_close_button.draw(screen)

        # layout areas
        left_x = x + 22
        top_y = y + 70
        left_w = int(w * 0.55)
        right_x = x + left_w + 28
        right_w = w - (right_x - x) - 22

        # headers
        monsters_label = self.bag_font.render("Monsters", True, (40, 20, 10))
        items_label = self.bag_font.render("Items", True, (40, 20, 10))
        screen.blit(monsters_label, (left_x, top_y - 28))
        screen.blit(items_label, (right_x, top_y - 28))

        # -------- LEFT: monster cards with banner --------
        card_h = 70
        card_gap = 12
        cur_y = top_y

        #removethis
        #print(pg.image.load("assets/images/UI/button_x.png"))

        monsters = getattr(self.game_manager.bag, "_monsters_data", [])
        for mon in monsters[:4]:  # show up to 4 (avoid overflow)
            # banner scaled to fit card area
            banner_w = left_w - 20
            banner_h = card_h
            banner = pg.transform.scale(self.mon_banner_img, (banner_w, banner_h))
            screen.blit(banner, (left_x, cur_y))

            # monster sprite
            spr_path = "assets/images/" + mon.get("sprite_path", "")
            try:
                
                spr = pg.image.load(spr_path).convert_alpha()
                SPR_SIZE = 52
                spr = pg.transform.scale(spr, (SPR_SIZE, SPR_SIZE))


                spr_x = left_x + 20
                spr_y = cur_y - 3 
                screen.blit(spr, (spr_x, spr_y))
            except Exception as e:
                print("Failed to load monster sprite:", spr_path, e)

            # name + level
            name = mon.get("name", "Unknown")
            lvl = mon.get("level", 1)
            hp = mon.get("hp", 0)
            max_hp = mon.get("max_hp", 1)

            name_s = self.bag_font.render(f"{name}", True, (20, 20, 20))
            lvl_s = self.bag_small_font.render(f"Lv{lvl}", True, (20, 20, 20))
            screen.blit(name_s, (left_x + 82, cur_y + 10))
            screen.blit(lvl_s, (left_x + banner_w - 52, cur_y + 12))

            # HP bar
            bar_x = left_x + 80
            bar_y = cur_y + 30
            bar_w = banner_w - 110
            bar_h = 8

            pg.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
            ratio = 0.0 if max_hp <= 0 else max(0.0, min(1.0, hp / max_hp))
            fill_w = int(bar_w * ratio)
            pg.draw.rect(screen, (70, 200, 90), (bar_x, bar_y, fill_w, bar_h), border_radius=4)

            hp_s = self.bag_small_font.render(f"HP {hp}/{max_hp}", True, (20, 20, 20))
            screen.blit(hp_s, (bar_x, bar_y + 11))

            cur_y += card_h + card_gap

        # -------- RIGHT: item list with icons --------
        items = getattr(self.game_manager.bag, "_items_data", [])
        row_h = 46
        cur_y = top_y

        for it in items[:7]:
            name = it.get("name", "Item")
            count = it.get("count", 0)

            icon_rel = it.get("sprite_path") or self.item_icon_map.get(name, "")
            icon_path = "assets/images/" + icon_rel

            try:
                icon = pg.image.load(icon_path).convert_alpha()
                ICON_SIZE = 38   # try 44 or 48

                icon = pg.transform.scale(icon, (ICON_SIZE, ICON_SIZE))
                screen.blit(icon, (right_x, cur_y + (row_h - ICON_SIZE)//2))

            except Exception as e:
                print("Failed to load item icon:", icon_path, e)

                

            name_s = self.bag_font.render(name, True, (40, 20, 10))
            cnt_s = self.bag_font.render(f"x{count}", True, (40, 20, 10))

            screen.blit(name_s, (right_x + 44, cur_y + 10))
            screen.blit(cnt_s, (right_x + right_w - cnt_s.get_width() - 10, cur_y + 10))

            cur_y += row_h


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
        Now: randomly picks a wild pokemon from self.wild_pokemon_pool.
        """
        if not self.near_bush:
            return

        # Pick a random pokemon template from the pool
        template = random.choice(self.wild_pokemon_pool)

        # Randomize its level in the given range
        level = random.randint(template["min_level"], template["max_level"])

        # Simple scaling for HP based on level (you can change this formula)
        max_hp = template["base_hp"] + (level - 1) * 5

        new_mon = {
            "name": template["name"],
            "hp": max_hp,
            "max_hp": max_hp,
            "level": level,
            "sprite_path": template["sprite_path"],
        }

        self.game_manager.bag._monsters_data.append(new_mon)
        Logger.info(f"Caught a wild {new_mon['name']}! Lv{new_mon['level']}")

        # optional SFX if you have one
        try:
            sound_manager.play_sound("SFX/POKEBALL_CAPTURE.wav", volume=0.7)
        except Exception:
            pass
