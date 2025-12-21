import pygame as pg
import random
from src.interface.components import Button
from src.utils import Logger
from src.entities.pokemon import Pokemon
from src.core.managers.game_manager import GameManager  
from src.core import GameManager
from src.scenes.scene import Scene
from src.core.services import scene_manager, input_manager
from src.utils import GameSettings
from typing import override
from src.sprites import BackgroundSprite, Sprite


class BattleScene(Scene):
    """
    Very simple turn-based battle:

    - Player and enemy both have HP.
    - Player turn first.
        - Press A to ATTACK
        - Press R to RUN (back to game)
    - After player attacks, enemy automatically attacks.
    - When either HP reaches 0, show win/lose message.
      Press SPACE to return to game.
    """

    def __init__(self) -> None:
        self.game_manager = GameManager.load("saves/game0.json")
        super().__init__()
        self.background = BackgroundSprite("backgrounds/background2.png")
        self.personal = Sprite("menu_sprites/menusprite16.png", (350,350))
        self.personal.rect.center = (
            GameSettings.SCREEN_WIDTH // 2 - 450,
            GameSettings.SCREEN_HEIGHT // 2 + 30
        
        )
        self.enemy = Sprite("menu_sprites/menusprite11.png", (400,400))
        self.enemy.rect.center = (
            GameSettings.SCREEN_WIDTH // 2 + 450,
            GameSettings.SCREEN_HEIGHT // 2 - 200
        
        )

        # whose turn?
        self.state: str = "player_turn"  # "enemy_turn", "player_win", "enemy_win"
        self.enemy_attack_timer: float = 0.0

        # UI stuff
        self.font_big = pg.font.Font("assets/fonts/Minecraft.ttf", 32)
        self.font_small = pg.font.Font("assets/fonts/Minecraft.ttf", 24)

        # -------- item overlay --------
        self.item_open = False
        self.item_btn = Button(
            "UI/button_backpack.png", "UI/button_backpack_hover.png",
            20, 20, 80, 80,
            self._open_items
        )


        self.item_panel_w, self.item_panel_h = 760, 430
        self.item_panel_x = (GameSettings.SCREEN_WIDTH - self.item_panel_w) // 2
        self.item_panel_y = (GameSettings.SCREEN_HEIGHT - self.item_panel_h) // 2
        self.item_close_rect = pg.Rect(self.item_panel_x + self.item_panel_w - 56, self.item_panel_y + 18, 40, 40)

        # close buttoM  
        x_size = 48
        x_x = self.item_panel_x + self.item_panel_w - x_size - 14
        x_y = self.item_panel_y + 14
        self.item_close_button = Button(
            "UI/button_x.png", "UI/button_x_hover.png",
            x_x, x_y, x_size, x_size,
            self._close_items
        )

        self.item_title_font = pg.font.Font("assets/fonts/Minecraft.ttf", 22)
        self.item_font = pg.font.Font("assets/fonts/Minecraft.ttf", 14)
        self._item_use_rects = []

        self.item_tab = "items"      # "items" or "pokemon"
        self.poke_filter = None      # None / "grass" / "fire" / "water"

        tab_w, tab_h = 120, 44
        self.item_items_tab_rect = pg.Rect(self.item_panel_x + 30, self.item_panel_y + 20, tab_w, tab_h)
        self.item_poke_tab_rect  = pg.Rect(self.item_panel_x + 30 + tab_w + 16, self.item_panel_y + 20, tab_w, tab_h)

        self.element_icon_cache = {}
        self.element_icon_size = 18


        # optional: map item names to icons (same idea as GameScene)
        self.item_icon_map = {
            "Potion": "ingame_ui/potion.png",
            "Coins": "ingame_ui/coin.png",
            "Pokeball": "ingame_ui/ball.png",
            "Heal Potion": "ingame_ui/options3.png",
            "Strength Potion": "ingame_ui/options1.png",
            "Defense Potion": "ingame_ui/options2.png",
        }

        # dynamic USE buttons per row
        self._item_use_buttons: list[Button] = []
        self._item_overlay_last_key = None  # used to rebuild buttons only when list changes

        # buffs that apply to NEXT action
        self.pending_atk_bonus = 0
        self.pending_def_bonus = 0

        self.wild_pokemon_pool = [
            {"name": "Bushmon",     "element": "grass", "base_hp": 60, "min_level": 2, "max_level": 5,  "sprite_path": "menu_sprites/menusprite1.png"},
            {"name": "Leaflynx",    "element": "grass", "base_hp": 65, "min_level": 2, "max_level": 6,  "sprite_path": "menu_sprites/menusprite2.png"},
            {"name": "Verdpuma",    "element": "grass", "base_hp": 75, "min_level": 3, "max_level": 7,  "sprite_path": "menu_sprites/menusprite3.png"},
            {"name": "Sproutlet",   "element": "grass", "base_hp": 45, "min_level": 1, "max_level": 3,  "sprite_path": "menu_sprites/menusprite15.png"},
            {"name": "Flutterleaf", "element": "grass", "base_hp": 70, "min_level": 3, "max_level": 7,  "sprite_path": "menu_sprites/menusprite16.png"},

            {"name": "Blazewing",   "element": "fire",  "base_hp": 95, "min_level": 6, "max_level": 10, "sprite_path": "menu_sprites/menusprite9.png"},
            {"name": "Serpflare",   "element": "fire",  "base_hp": 75, "min_level": 4, "max_level": 8,  "sprite_path": "menu_sprites/menusprite11.png"},
            {"name": "Sparkpup",    "element": "fire",  "base_hp": 55, "min_level": 1, "max_level": 4,  "sprite_path": "menu_sprites/menusprite7.png"},


            {"name": "Aquabit",     "element": "water", "base_hp": 60, "min_level": 2, "max_level": 6,  "sprite_path": "menu_sprites/menusprite12.png"},
            {"name": "Glidefin",    "element": "water", "base_hp": 65, "min_level": 2, "max_level": 6,  "sprite_path": "menu_sprites/menusprite13.png"},
            {"name": "Seascale",    "element": "water", "base_hp": 90, "min_level": 5, "max_level": 9,  "sprite_path": "menu_sprites/menusprite14.png"},
            {"name": "Frostfox",    "element": "water", "base_hp": 70, "min_level": 3, "max_level": 7,  "sprite_path": "menu_sprites/menusprite6.png"},

            {"name": "Nightmew",    "element": "grass",  "base_hp": 60, "min_level": 3, "max_level": 7,  "sprite_path": "menu_sprites/menusprite10.png"},
            {"name": "Rufffang",    "element": "grass",  "base_hp": 70, "min_level": 2, "max_level": 6,  "sprite_path": "menu_sprites/menusprite8.png"},
            {"name": "Brownbit",    "element": "grass","base_hp": 55, "min_level": 1, "max_level": 4,  "sprite_path": "menu_sprites/menusprite4.png"},
            {"name": "Pebblip",     "element": "grass","base_hp": 50, "min_level": 1, "max_level": 4,  "sprite_path": "menu_sprites/menusprite5.png"},
        ]  

        self.player_mon = Pokemon(
            name="Sproutlet",
            element="grass",
            level=1,
            max_hp=50,
            hp=50,
            attack=10,
            defense=2,
            sprite_path="menu_sprites/menusprite16.png",

            evo_level=5,
            evo_name="Flutterleaf",
            evo_sprite_path="menu_sprites/menusprite15.png",  # must be different asset
            evo_bonus_hp=25,
            evo_bonus_atk=6,
            evo_bonus_def=3
        )

        self.enemy_mon = Pokemon(
            name="Serpflare",
            element="fire",
            level=1,
            max_hp=40,
            hp=40,
            attack=8,
            defense=1,
            sprite_path="menu_sprites/menusprite11.png",
        )
        self.game_manager = GameManager.load("saves/game0.json")
        if self.game_manager is None:
            raise RuntimeError("Failed to load game manager for battle")

    def _sync_bag_from_save(self) -> None:
        gm = GameManager.load("saves/game0.json")
        if gm is not None:
            self.game_manager = gm

    
    def _open_items(self) -> None:
        self._sync_bag_from_save()
        self.item_open = True
        self.item_tab = "items"
        self.poke_filter = None
        self._item_overlay_last_key = None
        self._rebuild_item_overlay_buttons()

    def _close_items(self) -> None:
        self.item_open = False

    def _apply_item_effect(self, item_name: str) -> None:
    # Feel free to rename these to match YOUR shop item names exactly.
        if item_name == "Heal Potion":
        # immediate heal
            self.player_mon.heal(20)
        elif item_name == "Potion":
        # immediate heal
            self.player_mon.heal(10)
        elif item_name == "Strength Potion":
        # next attack bonus only
            self.pending_atk_bonus += 5
        elif item_name == "Rare Candy":
        # reduces next enemy hit only
            self.pending_atk_bonus += 10
        elif item_name == "Defense Potion":
        # reduces next enemy hit only
            self.pending_def_bonus += 3
        else:
        # other items do nothing in battle
            Logger.info(f"{item_name} cannot be used in battle.")

    def _get_element_icon(self, element: str) -> pg.Surface | None:
        element = (element or "").lower()
        if element in self.element_icon_cache:
            return self.element_icon_cache[element]
        path = f"assets/images/ingame_ui/{element}.png"
        try:
            img = pg.image.load(path).convert_alpha()
            img = pg.transform.scale(img, (self.element_icon_size, self.element_icon_size))
            self.element_icon_cache[element] = img
            return img
        except Exception:
            self.element_icon_cache[element] = None
            return None


    def _bag_items(self):
        return getattr(self.game_manager.bag, "_items_data", [])

    def _bag_count(self, name: str) -> int:
        for it in self._bag_items():
            if it.get("name") == name:
                return int(it.get("count", 0))
        return 0

    def _bag_remove(self, name: str, qty: int) -> bool:
        items = self._bag_items()
        for i, it in enumerate(items):
            if it.get("name") == name:
                cur = int(it.get("count", 0))
                if cur < qty:
                    return False
                it["count"] = cur - qty
                if it["count"] <= 0:
                    items.pop(i)
                return True
        return False

    def _use_heal_potion(self):
        if self._bag_remove("Heal Potion", 1):
            self.player_mon.heal(20)   

    def _use_strength_potion(self):
        if self._bag_remove("Strength Potion", 1):
            self.player_mon.attack += 5

    def _use_defense_potion(self):
        if self._bag_remove("Defense Potion", 1):
            self.player_mon.defense += 3

    @override
    def enter(self) -> None:
            # reload manager so items/monsters are fresh
        self.game_manager = GameManager.load("saves/game0.json")
        if self.game_manager is None:
            Logger.error("Battle: failed to load game manager")
            scene_manager.change_scene("game")
            return

        # ---- PLAYER MON from BAG ----
        mon = self._get_player_mon_from_bag()
        if mon is None:
            Logger.warning("No monsters in bag, cannot battle.")
            scene_manager.change_scene("game")
            return
        
        self.player_mon = Pokemon(
            name=mon.get("name", "PlayerMon"),
            element=mon.get("element", "grass"),
            level=int(mon.get("level", 1)),
            max_hp=int(mon.get("max_hp", 50)),
            hp=int(mon.get("hp", 50)),
            attack=10 + int(mon.get("level", 1)) * 2,
            defense=2 + int(mon.get("level", 1)) // 2,
            sprite_path=mon.get("sprite_path", "menu_sprites/menusprite1.png"),
            evo_level=5,
            evo_name=mon.get("name", "Mon") + " Evo",
            evo_sprite_path="menu_sprites/menusprite2.png",
            evo_bonus_hp=20,
            evo_bonus_atk=5,
            evo_bonus_def=3
        )


        # give element + battle stats (you can store element in bag later)
        # ---- ENEMY: from pending_encounter if exists, else random ----
        enc = getattr(self.game_manager, "pending_encounter", None)
        if isinstance(enc, dict):
            e_name = enc.get("name", "EnemyMon")
            e_elem = enc.get("element", "grass")
            e_lvl  = int(enc.get("level", max(1, self.player_mon.level)))
            e_hp   = int(enc.get("max_hp", 40 + e_lvl * 5))
            e_sprite = enc.get("sprite_path", "menu_sprites/menusprite11.png")

            # consume it so next battle doesn't reuse it
            self.game_manager.pending_encounter = None
            self.game_manager.save("saves/game0.json")
        else:
            template = random.choice(self.wild_pokemon_pool)
            e_name = template["name"]
            e_elem = template.get("element", "grass")
            e_lvl = max(1, self.player_mon.level)
            e_hp = template["base_hp"] + (e_lvl - 1) * 5
            e_sprite = template["sprite_path"]

        self.enemy_mon = Pokemon(
            name=e_name,
            element=e_elem,
            level=e_lvl,
            max_hp=e_hp,
            hp=e_hp,
            attack=8 + e_lvl * 2,
            defense=1 + e_lvl // 2,
            sprite_path=e_sprite
        )

        # rebuild sprites
        self.personal = Sprite(self.player_mon.sprite_path, (350, 350))
        self.personal.rect.center = (GameSettings.SCREEN_WIDTH // 2 - 450, GameSettings.SCREEN_HEIGHT // 2 + 30)

        self.enemy = Sprite(self.enemy_mon.sprite_path, (400, 400))
        self.enemy.rect.center = (GameSettings.SCREEN_WIDTH // 2 + 450, GameSettings.SCREEN_HEIGHT // 2 - 200)

        self.state = "player_turn"
        self.enemy_attack_timer = 0.0

        
    

    def _calc_raw_damage(self, attacker: Pokemon, defender: Pokemon) -> int:
        mult = self._type_multiplier(attacker.element, defender.element)
        return max(1, int(attacker.attack * mult))
    
    def _bag_items(self):
        return getattr(self.game_manager.bag, "_items_data", [])

    def _bag_count(self, name: str) -> int:
        for it in self._bag_items():
            if it.get("name") == name:
                return int(it.get("count", 0))
        return 0

    def _bag_remove(self, name: str, qty: int) -> bool:
        items = self._bag_items()
        for i, it in enumerate(items):
            if it.get("name") == name:
                cur = int(it.get("count", 0))
                if cur < qty:
                    return False
                it["count"] = cur - qty
                if it["count"] <= 0:
                    items.pop(i)
                return True
        return False

    def _use_heal_potion(self):
        if self._bag_remove("Heal Potion", 1):
            self.player_mon.heal(20)

    def _use_strength_potion(self):
        if self._bag_remove("Strength Potion", 1):
            self.player_mon.attack += 5

    def _use_defense_potion(self):
        if self._bag_remove("Defense Potion", 1):
            self.player_mon.defense += 3

    def _type_multiplier(self, atk_type: str, def_type: str) -> float:
        # water > fire, fire > grass, grass > water
        chart = {
            ("water", "fire"): 2.0,
            ("fire", "grass"): 2.0,
            ("grass", "water"): 2.0,
            ("fire", "water"): 1.5,
            ("grass", "fire"): 1.0,
            ("water", "grass"): 1.7,
        }
        return chart.get((atk_type, def_type), 1.0)

    @override
    def update(self, dt: float) -> None:
        #self._sync_bag_from_save()
        self.item_btn.update(dt)
        # always animate
        if hasattr(self, "player_anim") and self.player_anim:
            self.player_anim.update(dt)
        if hasattr(self, "enemy_anim") and self.enemy_anim:
            self.enemy_anim.update(dt)


        # items overlay open blocks battle input
        if self.item_open:
            self.item_close_button.update(dt)  # still hover effect is ok
            # rebuild buttons if item list changed
            self._rebuild_item_overlay_buttons()

            # update each USE button (hover + click)
            for b in self._item_use_buttons:
                b.update(dt)
            #return
            

            if input_manager.key_pressed(pg.K_ESCAPE):
                self._close_items()
                return
            
            mouse_now = pg.mouse.get_pressed()[0]
            click = mouse_now and (not getattr(self, "_mouse_prev", False))
            self._mouse_prev = mouse_now

            if click:
                mx, my = pg.mouse.get_pos()
                if self.item_items_tab_rect.collidepoint(mx, my):
                    self.item_tab = "items"
                elif self.item_poke_tab_rect.collidepoint(mx, my):
                    self.item_tab = "pokemon"

            return

            '''
            mouse_now = pg.mouse.get_pressed()[0]
            click = mouse_now and (not getattr(self, "_mouse_prev", False))
            self._mouse_prev = mouse_now

            if click:
                mx, my = pg.mouse.get_pos()
                if self.item_close_rect.collidepoint(mx, my):
                    self._close_items()
                    return

            # click USE buttons
                for idx, r in self._item_use_rects:
                    if r.collidepoint(mx, my):
                        items = getattr(self.game_manager.bag, "_items_data", [])
                        if 0 <= idx < len(items):
                            name = items[idx].get("name", "")
                            if self._bag_remove(name, 1):
                                self._apply_item_effect(name)
                                self.game_manager.save("saves/game0.json")
                        return
            return
            '''

        if self.state == "player_turn":
            if input_manager.key_pressed(pg.K_1):
                self._use_heal_potion()
            elif input_manager.key_pressed(pg.K_2):
                self._use_strength_potion()
            elif input_manager.key_pressed(pg.K_3):
                self._use_defense_potion()

            elif input_manager.key_pressed(pg.K_a):
                mult = self._type_multiplier(self.player_mon.element, self.enemy_mon.element)
                raw = self._calc_damage(self.player_mon, self.enemy_mon)
                Logger.info(f"ATTACK mult={mult} raw={raw} enemy_def={self.enemy_mon.defense}")

                raw = self._calc_damage(self.player_mon, self.enemy_mon)
                Logger.info(f"ATTACK {self.player_mon.name}({self.player_mon.element}) -> "
                        f"{self.enemy_mon.name}({self.enemy_mon.element}) "
                        f"atk={self.player_mon.attack} mult={self._type_multiplier(self.player_mon.element, self.enemy_mon.element)} "
                        f"raw={raw} enemy_def={self.enemy_mon.defense} enemy_hp_before={self.enemy_mon.hp}")

                dmg = self.enemy_mon.take_damage(raw)

                Logger.info(f"ATTACK dealt={dmg} enemy_hp_after={self.enemy_mon.hp}")

                #self.pending_atk_bonus = 0 
                #self.enemy_mon.take_damage(raw)

                if self.enemy_mon.hp <= 0:
                    self.state = "player_win"
                else:
                    self.state = "enemy_turn"
                    self.enemy_attack_timer = 0.5

            elif input_manager.key_pressed(pg.K_r):
                scene_manager.change_scene("game")

        elif self.state == "enemy_turn":
            self.enemy_attack_timer -= dt
            if self.enemy_attack_timer <= 0:
                raw = self._calc_damage(self.enemy_mon, self.player_mon)

                # apply defense bonus ONLY for this one hit
                if self.pending_def_bonus:
                    old_def = self.player_mon.defense
                    self.player_mon.defense += self.pending_def_bonus
                    self.pending_def_bonus = 0
                    raw = self._calc_damage(self.enemy_mon, self.player_mon)
                    Logger.info(f"ENEMY {self.enemy_mon.name}({self.enemy_mon.element}) -> "
            f"{self.player_mon.name}({self.player_mon.element}) "
            f"atk={self.enemy_mon.attack} mult={self._type_multiplier(self.enemy_mon.element, self.player_mon.element)} "
            f"raw={raw} player_def={self.player_mon.defense} player_hp_before={self.player_mon.hp}")

                    dmg = self.player_mon.take_damage(raw)

                    Logger.info(f"ENEMY dealt={dmg} player_hp_after={self.player_mon.hp}")

                    #self.player_mon.take_damage(raw)
                    self.player_mon.defense = old_def
                else:
                    self.player_mon.take_damage(raw)

                if self.player_mon.hp <= 0:
                    self.state = "enemy_win"
                else:
                    self.state = "player_turn"


        elif self.state == "player_win":
            # After result, press SPACE to go back to game scene
            if input_manager.key_pressed(pg.K_SPACE):
                self.player_mon.level += 1
                self.player_mon.try_evolve()
                # reward: level up + evolve
                
                monsters = getattr(self.game_manager.bag, "_monsters_data", [])
                if monsters:
                    monsters[0]["name"] = self.player_mon.name
                    monsters[0]["level"] = self.player_mon.level
                    monsters[0]["max_hp"] = self.player_mon.max_hp
                    monsters[0]["hp"] = self.player_mon.hp
                    monsters[0]["sprite_path"] = self.player_mon.sprite_path
                #evolved = self.player_mon.try_evolve()
                #if evolved:
                    # rebuild sprite to show new asset
                    #self.personal = Sprite(self.player_mon.sprite_path, (350, 350))
                    #self.personal.rect.center = (GameSettings.SCREEN_WIDTH // 2 - 450, GameSettings.SCREEN_HEIGHT // 2 + 30)

                
                self.game_manager.save("saves/game0.json")
                scene_manager.change_scene("game")
        
       


    
    
    def _calc_damage(self, attacker, defender) -> int:
        mult = self._type_multiplier(attacker.element, defender.element)
        # base damage from attack, then element multiplier
        base = int(attacker.attack * mult)
        return max(1, base)   # defender defense handled in take_damage()


    def _get_player_mon_from_bag(self):
        monsters = getattr(self.game_manager.bag, "_monsters_data", [])
        if not monsters:
            return None
        return monsters[0]  # simplest: first monster



    @override
    def draw(self, screen: pg.Surface) -> None:
        w, h = GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT
        
        # Background
        self.background.draw(screen)
        # --- Enemy HP bar (top-right) ---
        # top-left items button
        self.item_btn.draw(screen)

        bar_w, bar_h = 200, 20
        enemy_x = w - bar_w - 60
        enemy_y = 40
        #pg.draw.rect(screen, (0, 0, 0), (enemy_x, enemy_y, bar_w, bar_h), 2)
        #enemy_ratio = self.enemy_mon.hp / self.enemy_mon.max_hp

  
        enemy_text = self.font_small.render(
            f"{self.enemy_mon.name} ({self.enemy_mon.hp}/{self.enemy_mon.element}) HP: {self.enemy_mon.hp}/{self.enemy_mon.max_hp}", True, (0, 0, 0)
        )
        player_text = self.font_small.render(
            f"Player HP: {self.player_mon.hp}/{self.player_mon.max_hp}", 
            True, (0, 0, 0)
        )

        screen.blit(enemy_text, (enemy_x, enemy_y - 25))

        # --- Player HP bar (bottom-left) ---
        self.personal.draw(screen)
        self.enemy.draw(screen)
        player_x = 60
        player_y = h - 120
        #pg.draw.rect(screen, (0, 0, 0), (player_x, player_y, bar_w, bar_h), 2)
        #player_ratio = self.player_mon.hp / self.player_mon.max_hp


        '''
        pg.draw.rect(
            screen,
            (0, 180, 60),
            (player_x + 2, player_y + 2, int((bar_w - 4) * player_ratio), bar_h - 4),
        )
        '''
        player_text = self.font_small.render(
            f"Player HP: {self.player_mon.hp}/{self.player_mon.max_hp}", True, (0, 0, 0)
        )
        screen.blit(player_text, (player_x, player_y - 25))

        # --- Placeholder monsters (replace with sprites later) ---
        # PLAYER_MONSTER
        #pg.draw.rect(screen, (40, 140, 40), (120, h - 260, 96, 96))
        # ENEMY_MONSTER
        #pg.draw.rect(screen, (140, 40, 40), (w - 220, 140, 96, 96))

        # --- Bottom message box / options ---
        box_h = 100
        pg.draw.rect(screen, (0, 0, 0), (0, h - box_h, w, box_h))
        pg.draw.rect(screen, (30, 30, 30), (4, h - box_h + 4, w - 8, box_h - 8))

        if self.state == "player_turn":
            line1 = "Your turn!"
            line2 = "Press A to ATTACK   |   Press R to RUN"
        elif self.state == "enemy_turn":
            line1 = "Enemy turn..."
            line2 = "Enemy is preparing an attack!"
        elif self.state == "player_win":
            line1 = "You won!"
            line2 = "Press SPACE to return."
        else:  # enemy_win
            line1 = "You lost..."
            line2 = "Press SPACE to return."

        txt1 = self.font_big.render(line1, True, (255, 255, 255))
        txt2 = self.font_small.render(line2, True, (255, 255, 255))
        screen.blit(txt1, (40, h - box_h + 20))
        screen.blit(txt2, (40, h - box_h + 60))

        h = self._bag_count("Heal Potion")
        s = self._bag_count("Strength Potion")
        d = self._bag_count("Defense Potion")
        line2 = f"A=ATTACK  1=HEAL({h})  2=STR({s})  3=DEF({d})  R=RUN"

        if self.state == "player_turn":
            h = self._bag_count("Heal Potion")
            s = self._bag_count("Strength Potion")
            d = self._bag_count("Defense Potion")
            line1 = "Your turn!"
            line2 = f"A=ATTACK | 1=HEAL({h}) 2=STR({s}) 3=DEF({d}) | R=RUN"

        
        enemy_text = self.font_small.render(
            f"{self.enemy_mon.name} [{self.enemy_mon.element}] HP: {self.enemy_mon.hp}/{self.enemy_mon.max_hp}",
            True, (0, 0, 0)
        )
        player_text = self.font_small.render(
            f"{self.player_mon.name} [{self.player_mon.element}] Lv{self.player_mon.level} HP: {self.player_mon.hp}/{self.player_mon.max_hp}",
            True, (0, 0, 0)
        )

        if self.item_open:
            self._draw_items_overlay(screen)   


    def _draw_items_overlay(self, screen: pg.Surface) -> None:
        # darken background
        dim = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pg.SRCALPHA)
        dim.fill((0, 0, 0, 140))
        screen.blit(dim, (0, 0))

        x, y, w, h = self.item_panel_x, self.item_panel_y, self.item_panel_w, self.item_panel_h
        panel = pg.Rect(x, y, w, h)

        # panel background
        pg.draw.rect(screen, (235, 160, 70), panel, border_radius=10)
        pg.draw.rect(screen, (60, 35, 20), panel, 4, border_radius=10)

        # title
        #title = self.item_title_font.render("BAG", True, (40, 20, 10))
        #screen.blit(title, (x + 18, y + 14))

        # close button
        self.item_close_button.draw(screen)

        # ---- tabs (draw on TOP of panel) ----
        def tab_color(active: bool):
            return (250, 235, 200) if active else (210, 190, 150)

        pg.draw.rect(screen, tab_color(self.item_tab == "items"), self.item_items_tab_rect, border_radius=6)
        pg.draw.rect(screen, tab_color(self.item_tab == "pokemon"), self.item_poke_tab_rect, border_radius=6)
        pg.draw.rect(screen, (0, 0, 0), self.item_items_tab_rect, 2, border_radius=6)
        pg.draw.rect(screen, (0, 0, 0), self.item_poke_tab_rect, 2, border_radius=6)

        t1 = self.item_title_font.render("Items", True, (0, 0, 0))
        t2 = self.item_title_font.render("Pokemon", True, (0, 0, 0))
        screen.blit(t1, (self.item_items_tab_rect.centerx - t1.get_width() // 2,
                     self.item_items_tab_rect.centery - t1.get_height() // 2))
        screen.blit(t2, (self.item_poke_tab_rect.centerx - t2.get_width() // 2,
                     self.item_poke_tab_rect.centery - t2.get_height() // 2))

        # ---- route pages ----
        if self.item_tab == "items":
            self._draw_item_page(screen)
        else:
            self._draw_pokemon_page(screen)


    def _draw_item_page(self, screen: pg.Surface) -> None:
        x, y, w, h = self.item_panel_x, self.item_panel_y, self.item_panel_w, self.item_panel_h

        # header
        items_label = self.item_font.render("Items", True, (40, 20, 10))
        screen.blit(items_label, (x + 40, y + 70))

        items = getattr(self.game_manager.bag, "_items_data", [])

        list_x = x + 40
        list_y = y + 100
        row_h = 56
        max_rows = 6

        for idx, it in enumerate(items[:max_rows]):
            ry = list_y + idx * (row_h + 10)
            row_rect = pg.Rect(list_x, ry, w - 80, row_h)

            # row background
            pg.draw.rect(screen, (250, 235, 200), row_rect, border_radius=8)
            pg.draw.rect(screen, (0, 0, 0), row_rect, 2, border_radius=8)

            name = it.get("name", "Item")
            count = int(it.get("count", 0))

            # icon
            icon_rel = it.get("sprite_path") or self.item_icon_map.get(name, "")
            if icon_rel:
                icon_path = "assets/images/" + icon_rel
                try:
                    icon = pg.image.load(icon_path).convert_alpha()
                    ICON_SIZE = 40
                    icon = pg.transform.scale(icon, (ICON_SIZE, ICON_SIZE))
                    screen.blit(icon, (row_rect.x + 14, ry + (row_h - ICON_SIZE)//2))
                except Exception as e:
                    print("Failed to load item icon:", icon_path, e)

            # name + count
            name_s = self.item_font.render(name, True, (40, 20, 10))
            cnt_s  = self.item_font.render(f"x{count}", True, (40, 20, 10))
            screen.blit(name_s, (row_rect.x + 14 + 52, ry + 18))
            screen.blit(cnt_s, (row_rect.right - cnt_s.get_width() - 150, ry + 18))

            # USE button (only draw if exists)
            if idx < len(self._item_use_buttons):
                self._item_use_buttons[idx].draw(screen)

                # text "USE"
                btn = self._item_use_buttons[idx]
                label = self.item_font.render("USE", True, (0, 0, 0))
                lx = btn.hitbox.x + (btn.hitbox.width - label.get_width()) // 2
                ly = btn.hitbox.y + (btn.hitbox.height - label.get_height()) // 2
                screen.blit(label, (lx, ly))


    def _bag_monsters(self):
        return getattr(self.game_manager.bag, "_monsters_data", [])

    def _draw_pokemon_page(self, screen: pg.Surface) -> None:
        x, y, w, h = self.item_panel_x, self.item_panel_y, self.item_panel_w, self.item_panel_h

        # filter buttons (icons)
        fx = x + 40
        fy = y + 80
        gap = 14
        elems = ["grass", "fire", "water"]

        self._filter_rects = []
        for i, e in enumerate(elems):
            r = pg.Rect(fx + i*(self.element_icon_size + gap + 12), fy, self.element_icon_size + 12, self.element_icon_size + 12)
            pg.draw.rect(screen, (250,235,200), r, border_radius=6)
            pg.draw.rect(screen, (0,0,0), r, 2, border_radius=6)
            icon = self._get_element_icon(e)
            if icon:
                screen.blit(icon, (r.x + 6, r.y + 6))
            self._filter_rects.append((e, r))

        # "ALL" filter
        all_r = pg.Rect(fx + 3*(self.element_icon_size + gap + 12), fy, 70, self.element_icon_size + 12)
        pg.draw.rect(screen, (250,235,200), all_r, border_radius=6)
        pg.draw.rect(screen, (0,0,0), all_r, 2, border_radius=6)
        all_t = self.item_font.render("ALL", True, (0,0,0))
        screen.blit(all_t, (all_r.centerx - all_t.get_width()//2, all_r.centery - all_t.get_height()//2))
        self._filter_rects.append((None, all_r))

        # handle clicks
        mouse_now = pg.mouse.get_pressed()[0]
        click = mouse_now and (not getattr(self, "_poke_mouse_prev", False))
        self._poke_mouse_prev = mouse_now
        if click:
            mx, my = pg.mouse.get_pos()
            for val, r in self._filter_rects:
                if r.collidepoint(mx, my):
                    self.poke_filter = val

        mons = self._bag_monsters()
        if self.poke_filter:
            mons = [m for m in mons if m.get("element") == self.poke_filter]

        # list cards
        list_x = x + 40
        list_y = y + 120
        row_h = 70
        max_rows = 4

        self._poke_select_rects = []
        for idx, mon in enumerate(mons[:max_rows]):
            ry = list_y + idx*(row_h + 12)
            row = pg.Rect(list_x, ry, w - 80, row_h)
            pg.draw.rect(screen, (250,235,200), row, border_radius=8)
            pg.draw.rect(screen, (0,0,0), row, 2, border_radius=8)

            name = mon.get("name", "Mon")
            lvl  = int(mon.get("level", 1))
            hp   = int(mon.get("hp", 0))
            mxhp = int(mon.get("max_hp", 1))
            elem = mon.get("element", "grass")

            # sprite
            spr_path = "assets/images/" + mon.get("sprite_path", "")
            try:
                spr = pg.image.load(spr_path).convert_alpha()
                spr = pg.transform.scale(spr, (52, 52))
                screen.blit(spr, (row.x + 14, row.y + 8))
            except Exception:
                pass

            # texts
            name_t = self.item_font.render(f"{name}  Lv{lvl}", True, (0,0,0))
            screen.blit(name_t, (row.x + 80, row.y + 12))

            # hp bar
            bar_x = row.x + 80
            bar_y = row.y + 36
            bar_w = row.w - 160
            bar_hh = 8
            pg.draw.rect(screen, (60,60,60), (bar_x, bar_y, bar_w, bar_hh), border_radius=4)
            ratio = 0.0 if mxhp <= 0 else max(0.0, min(1.0, hp/mxhp))
            pg.draw.rect(screen, (70,200,90), (bar_x, bar_y, int(bar_w*ratio), bar_hh), border_radius=4)

            hp_t = self.item_font.render(f"HP {hp}/{mxhp}", True, (0,0,0))
            screen.blit(hp_t, (bar_x, bar_y + 12))

            icon = self._get_element_icon(elem)
            if icon:
                screen.blit(icon, (row.right - 28, bar_y + 10))

            # selectable rect
            self._poke_select_rects.append((mon, row))

    #    click select to switch player_mon
        if click:
            mx, my = pg.mouse.get_pos()
            for mon, r in getattr(self, "_poke_select_rects", []):
                if r.collidepoint(mx, my):
                    self._switch_player_mon(mon)
                    self.item_open = False
                    return

    def _switch_player_mon(self, mon: dict) -> None:
        self.player_mon = Pokemon(
            name=mon.get("name", "PlayerMon"),
            element=mon.get("element", "grass"),
            level=int(mon.get("level", 1)),
            max_hp=int(mon.get("max_hp", 50)),
            hp=int(mon.get("hp", 50)),
            attack=10 + int(mon.get("level", 1)) * 2,
            defense=2 + int(mon.get("level", 1)) // 2,
            sprite_path=mon.get("sprite_path", "menu_sprites/menusprite1.png"),
            evo_level=5,
            evo_name=mon.get("name", "Mon") + " Evo",
            evo_sprite_path="menu_sprites/menusprite2.png",
            evo_bonus_hp=20,
            evo_bonus_atk=5,
            evo_bonus_def=3
        )

        # rebuild sprite to match new player pokemon
        self.personal = Sprite(self.player_mon.sprite_path, (350,350))
        self.personal.rect.center = (
            GameSettings.SCREEN_WIDTH // 2 - 450,
            GameSettings.SCREEN_HEIGHT // 2 + 30
        )


    def _rebuild_item_overlay_buttons(self) -> None:
        items = getattr(self.game_manager.bag, "_items_data", [])
        # build a key that changes when items change
        key = tuple((it.get("name", ""), int(it.get("count", 0))) for it in items)

        if key == self._item_overlay_last_key:
            return
        self._item_overlay_last_key = key

        self._item_use_buttons = []

        
        x, y, w, h = self.item_panel_x, self.item_panel_y, self.item_panel_w, self.item_panel_h
        list_x = x + 40
        list_y = y + 100
        row_h = 56
        max_rows = 6

        # button size in each row (right side)
        use_w, use_h = 110, 44

        for idx, it in enumerate(items[:max_rows]):
            ry = list_y + idx * (row_h + 10)
            row_rect = pg.Rect(list_x, ry, w - 80, row_h)

            btn_x = row_rect.right - use_w - 16
            btn_y = ry + (row_h - use_h) // 2

            
            b = Button(
                "UI/raw/UI_Flat_Button02a_4.png",   # normal
                "UI/raw/UI_Flat_Button02a_1.png",   # hover
                btn_x, btn_y, use_w, use_h,
                lambda i=idx: self._use_item_from_overlay(i)
            )
            self._item_use_buttons.append(b)

    def _can_use_item_in_battle(self, name: str) -> bool:
        return name in {
            "Potion",
            "Heal Potion",
            "Strength Potion",
            "Defense Potion",
            "Rare Candy",
            # add more battle-usable items here!!!!
        }


    def _use_item_from_overlay(self, idx: int) -> None:
        items = getattr(self.game_manager.bag, "_items_data", [])
        if idx < 0 or idx >= len(items):
            return

        name = items[idx].get("name", "")
        count = int(items[idx].get("count", 0))
        if count <= 0:
            return

        if not self._can_use_item_in_battle(name):
            Logger.info(f"{name} cannot be used in battle.")
            return

        # remove 1 from bag
        if not self._bag_remove(name, 1):
            return

        # apply effect
        self._apply_item_effect(name)

        # save so game scene sees updated counts
        self.game_manager.save("saves/game0.json")

        # refresh overlay buttons/text
        self._item_overlay_last_key = None
        self._rebuild_item_overlay_buttons()
