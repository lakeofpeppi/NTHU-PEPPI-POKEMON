import pygame as pg
from src.utils import load_sound, GameSettings

class SoundManager:
    def __init__(self):
        pg.mixer.init()
        pg.mixer.set_num_channels(GameSettings.MAX_CHANNELS)

        self.current_bgm = None

        # store volumes separately so UI can change them
        self.bgm_volume = GameSettings.AUDIO_VOLUME
        self.sfx_volume = GameSettings.AUDIO_VOLUME

    # ---------- BGM ----------
    def play_bgm(self, filepath: str):
        if self.current_bgm:
            self.current_bgm.stop()
        audio = load_sound(filepath)
        audio.set_volume(self.bgm_volume)
        audio.play(-1)
        self.current_bgm = audio

    def set_bgm_volume(self, volume: float):
        """volume in [0,1]"""
        self.bgm_volume = max(0.0, min(1.0, volume))
        if self.current_bgm:
            self.current_bgm.set_volume(self.bgm_volume)

    def get_bgm_volume(self) -> float:
        return self.bgm_volume

    # ---------- SFX ----------
    def set_sfx_volume(self, volume: float):
        self.sfx_volume = max(0.0, min(1.0, volume))

    def get_sfx_volume(self) -> float:
        return self.sfx_volume

    def play_sound(self, filepath, volume: float = 1.0):
        """volume is a per-sound multiplier, final = self.sfx_volume * volume"""
        sound = load_sound(filepath)
        sound.set_volume(self.sfx_volume * volume)
        sound.play()

    # ---------- Global controls ----------
    def pause_all(self):
        pg.mixer.pause()

    def resume_all(self):
        pg.mixer.unpause()

    def stop_all_sounds(self):
        pg.mixer.stop()
        self.current_bgm = None
