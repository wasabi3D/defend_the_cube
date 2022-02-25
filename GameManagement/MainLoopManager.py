from numpy import isin
import pygame
import GameManagement.SceneManager as SceneManager
from GameManagement.Exceptions import *
import GameManagement.singleton as sing
import typing


class GameRoot:
    def __init__(self, screen_dimension: tuple[int, int], default_background_color: tuple[int, int, int], title: str,
                 fps_limit=60):
        sing.ROOT = self
        self.display: pygame.Surface = pygame.display.set_mode(screen_dimension)
        pygame.display.set_caption(title)
        self.scenes: list[SceneManager.Scene] = []
        self.background: tuple[int, int, int] = default_background_color
        self.fps_limit = fps_limit
        self.clock = pygame.time.Clock()
        self.delta = 0
        self.screen_dim = screen_dimension

    def register(self, scene: SceneManager.Scene, index=-1):
        if index < 0:
            self.scenes.append(scene)
        else:
            self.scenes.insert(index, scene)

    def mainloop(self):
        done = False

        if len(self.scenes) == 0:
            raise NoAvailableSceneException()

        cur_scene: SceneManager.Scene = self.scenes[0]

        if not isinstance(cur_scene, SceneManager.Scene):
            raise NotASceneObjectException(f"First scene is not a scene object but it's a\
            {type(cur_scene)}.")

        cur_scene.start()
        self.delta = 0
        while not done:
            self.delta = pygame.time.get_ticks()
            # ___START___
            cur_scene.start_of_frame()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
            # ___________

            # ___MAIN UPDATE___
            cur_scene.update()
            # _________________

            # __ BLIT THINGS ON THE SCREEN __
            self.display.fill(self.background)
            cur_scene.blit_objects(self.display)
            pygame.display.update()
            self.clock.tick(self.fps_limit)
