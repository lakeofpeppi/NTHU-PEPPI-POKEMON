import pygame as pg

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
        # Basic stats
        self.player_max_hp = 50
        self.player_hp = 50

        self.enemy_max_hp = 40
        self.enemy_hp = 40

        # whose turn?
        self.state: str = "player_turn"  # "enemy_turn", "player_win", "enemy_win"
        self.enemy_attack_timer: float = 0.0

        # UI stuff
        self.font_big = pg.font.Font("assets/fonts/Minecraft.ttf", 32)
        self.font_small = pg.font.Font("assets/fonts/Minecraft.ttf", 24)

       

    @override
    def enter(self) -> None:
        # Reset HP every time we enter (simple demo)
        self.player_hp = self.player_max_hp
        self.enemy_hp = self.enemy_max_hp
        self.state = "player_turn"
        self.enemy_attack_timer = 0.0

    @override
    def update(self, dt: float) -> None:
        if self.state == "player_turn":
            # Attack with A
            if input_manager.key_pressed(pg.K_a):
                self.enemy_hp -= 10
                if self.enemy_hp <= 0:
                    self.enemy_hp = 0
                    self.state = "player_win"
                else:
                    # enemy will attack after a short delay
                    self.state = "enemy_turn"
                    self.enemy_attack_timer = 0.5

            # Run away with R
            elif input_manager.key_pressed(pg.K_r):
                scene_manager.change_scene("game")

        elif self.state == "enemy_turn":
            # Simple timer so enemy attack isn't instant
            self.enemy_attack_timer -= dt
            if self.enemy_attack_timer <= 0:
                self.player_hp -= 8
                if self.player_hp <= 0:
                    self.player_hp = 0
                    self.state = "enemy_win"
                else:
                    self.state = "player_turn"

        elif self.state in ("player_win", "enemy_win"):
            # After result, press SPACE to go back to game scene
            if input_manager.key_pressed(pg.K_SPACE):
                scene_manager.change_scene("game")

    @override
    def draw(self, screen: pg.Surface) -> None:
        w, h = GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT
        
        # Background
        self.background.draw(screen)
        # --- Enemy HP bar (top-right) ---
        
        bar_w, bar_h = 200, 20
        enemy_x = w - bar_w - 60
        enemy_y = 40
        #pg.draw.rect(screen, (0, 0, 0), (enemy_x, enemy_y, bar_w, bar_h), 2)
        enemy_ratio = self.enemy_hp / self.enemy_max_hp
        '''
        pg.draw.rect(
            screen,
            (200, 0, 0),
            (enemy_x + 2, enemy_y + 2, int((bar_w - 4) * enemy_ratio), bar_h - 4),
        )
        '''
        enemy_text = self.font_small.render(
            f"Enemy HP: {self.enemy_hp}/{self.enemy_max_hp}", True, (0, 0, 0)
        )
        screen.blit(enemy_text, (enemy_x, enemy_y - 25))

        # --- Player HP bar (bottom-left) ---
        self.personal.draw(screen)
        self.enemy.draw(screen)
        player_x = 60
        player_y = h - 120
        #pg.draw.rect(screen, (0, 0, 0), (player_x, player_y, bar_w, bar_h), 2)
        player_ratio = self.player_hp / self.player_max_hp
        '''
        pg.draw.rect(
            screen,
            (0, 180, 60),
            (player_x + 2, player_y + 2, int((bar_w - 4) * player_ratio), bar_h - 4),
        )
        '''
        player_text = self.font_small.render(
            f"Player HP: {self.player_hp}/{self.player_max_hp}", True, (0, 0, 0)
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
