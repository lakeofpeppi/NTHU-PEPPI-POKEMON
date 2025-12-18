
'''
import pygame as pg

from src.scenes.scene import Scene
from src.utils import Logger

class SceneManager:
    
    _scenes: dict[str, Scene]
    _current_scene: Scene | None = None
    _next_scene: str | None = None
    
    def __init__(self):
        Logger.info("Initializing SceneManager")
        self._scenes = {}
        
    def register_scene(self, name: str, scene: Scene) -> None:
        self._scenes[name] = scene
        
    def change_scene(self, scene_name: str) -> None:
        if scene_name in self._scenes:
            Logger.info(f"Changing scene to '{scene_name}'")
            self._next_scene = scene_name
        else:
            raise ValueError(f"Scene '{scene_name}' not found")
            
    def update(self, dt: float) -> None:
        # Handle scene transition
        if self._next_scene is not None:
            self._perform_scene_switch()
            
        # Update current scene
        if self._current_scene:
            self._current_scene.update(dt)
            
    def draw(self, screen: pg.Surface) -> None:
        if self._current_scene:
            self._current_scene.draw(screen)
            
    def _perform_scene_switch(self) -> None:
        if self._next_scene is None:
            return
            
        # Exit current scene
        if self._current_scene:
            self._current_scene.exit()
        
        self._current_scene = self._scenes[self._next_scene]
        
        # Enter new scene
        if self._current_scene:
            Logger.info(f"Entering {self._next_scene} scene")
            self._current_scene.enter()
            
        # Clear the transition request
        self._next_scene = None
        

        
        '''

import pygame as pg

from src.scenes.scene import Scene
from src.scenes.transition_scene import TransitionScene
from src.utils import Logger


class SceneManager:
    _scenes: dict[str, Scene]
    _current_scene: Scene | None = None
    _next_scene: str | None = None

    # NEW: transition state
    _transition: TransitionScene | None = None
    _transition_target: str | None = None
    _did_swap: bool = False

    def __init__(self):
        Logger.info("Initializing SceneManager")
        self._scenes = {}
        self._current_scene = None
        self._next_scene = None

        self._transition = None
        self._transition_target = None
        self._did_swap = False

    def register_scene(self, name: str, scene: Scene) -> None:
        self._scenes[name] = scene

    # NEW: optional args but old calls still work
    def change_scene(self, scene_name: str, transition: bool = False, duration: float = 0.25) -> None:
        if scene_name not in self._scenes:
            raise ValueError(f"Scene '{scene_name}' not found")
        self._next_scene = scene_name
        self._use_transition = transition
        self._transition_duration = duration

        # If no current scene yet, do immediate switch (prevents black screen)
        if self._current_scene is None:
            Logger.info(f"Changing scene to '{scene_name}' (initial)")
            self._next_scene = scene_name
            return

        # If currently transitioning, ignore new requests
        if self._transition is not None:
            return

        if transition:
            Logger.info(f"Changing scene to '{scene_name}' with transition")
            self._transition_target = scene_name
            self._did_swap = False
            self._transition = TransitionScene(self._current_scene, self._scenes[scene_name], duration=duration)
        else:
            Logger.info(f"Changing scene to '{scene_name}' (no transition)")
            self._next_scene = scene_name

    def update(self, dt: float) -> None:
        # 1) Handle normal scene switch
        if self._next_scene is not None and self._transition is None:
            self._perform_scene_switch()

        # 2) Handle transition
        if self._transition is not None:
            self._transition.update(dt)

            # swap moment: when fade-out finished
            if (not self._did_swap) and self._transition.swapped:
                self._did_swap = True
                self._perform_scene_switch(use_target=self._transition_target)

            # done moment
            if self._transition.done:
                self._transition = None
                self._transition_target = None
                self._did_swap = False
            return

        # 3) Normal update
        if self._current_scene:
            self._current_scene.update(dt)

    def draw(self, screen: pg.Surface) -> None:
        if self._transition is not None:
            self._transition.draw(screen)
            return

        if self._current_scene:
            self._current_scene.draw(screen)

    def _perform_scene_switch(self, use_target: str | None = None) -> None:
        target = use_target if use_target is not None else self._next_scene
        if target is None:
            return

        # Exit current
        if self._current_scene:
            self._current_scene.exit()

        self._current_scene = self._scenes[target]

        # Enter new
        if self._current_scene:
            Logger.info(f"Entering {target} scene")
            self._current_scene.enter()

        # Clear normal switch request
        if use_target is None:
            self._next_scene = None
