import pygame
import GameManagement.SceneManager as SceneManager
from GameManagement.Exceptions import *
import GameManagement.singleton as sing


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
        self.key_ups = []
        self.key_downs = []
        self.mouse_ups: list[bool, bool, bool] = [False, False, False]
        self.mouse_downs: list[bool, bool, bool] = [False, False, False]

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
            t = pygame.time.get_ticks()
            self.key_ups.clear()
            self.key_downs.clear()
            self.mouse_ups = [False, False, False]
            self.mouse_downs = [False, False, False]
            # ___START___
            cur_scene.start_of_frame()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                elif event.type == pygame.KEYDOWN:
                    self.key_downs.append(event.key)
                elif event.type == pygame.KEYUP:
                    self.key_ups.append(event.key)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button > 3:  # MOUSE SCROLL
                        continue
                    self.mouse_ups[event.button - 1] = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button > 3:  # MOUSE SCROLL
                        continue
                    self.mouse_downs[event.button - 1] = True
            # ___________

            # ___MAIN UPDATE___
            cur_scene.update()
            # _________________

            # __ BLIT THINGS ON THE SCREEN __
            self.display.fill(self.background)
            cur_scene.blit_objects(self.display)
            pygame.display.update()
            self.delta = (pygame.time.get_ticks() - t) / 1000
            self.clock.tick(self.fps_limit)
