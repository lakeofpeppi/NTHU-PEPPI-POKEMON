from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Pokemon:
    name: str
    element: str                 # "water" | "fire" | "grass"
    level: int
    max_hp: int
    hp: int
    attack: int
    defense: int
    sprite_path: str

    evolved: bool = False
    evo_level: int = 5
    evo_name: str = ""
    evo_sprite_path: str = ""
    evo_bonus_hp: int = 20
    evo_bonus_atk: int = 5
    evo_bonus_def: int = 3

    def heal(self, amount: int) -> None:
        self.hp = min(self.max_hp, self.hp + amount)

    def take_damage(self, raw_damage: int) -> int:
        # defense reduces damage
        dmg = max(1, raw_damage - self.defense)
        self.hp = max(0, self.hp - dmg)
        return dmg

    def try_evolve(self) -> bool:
        if self.evolved:
            return False
        if self.level < self.evo_level:
            return False
        # evolve!
        self.evolved = True
        if self.evo_name:
            self.name = self.evo_name
        if self.evo_sprite_path:
            self.sprite_path = self.evo_sprite_path
        self.max_hp += self.evo_bonus_hp
        self.attack += self.evo_bonus_atk
        self.defense += self.evo_bonus_def
        self.hp = self.max_hp
        return True
