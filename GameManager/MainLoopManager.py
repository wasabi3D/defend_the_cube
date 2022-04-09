import pygame
import GameManager.singleton as sing
import GameManager.util as util
from typing import Optional
from collections import OrderedDict


class GameRoot:
    def __init__(self, screen_dimension: tuple[int, int], default_background_color: tuple[int, int, int], title: str,
                 resources_root_path: str, camera_pos: pygame.Vector2, fps_limit=60, display_flag=pygame.SCALED):
        pygame.init()
        sing.ROOT = self
        self.display: pygame.Surface = pygame.display.set_mode(screen_dimension, flags=display_flag)
        pygame.display.set_caption(title)
        self.background: tuple[int, int, int] = default_background_color
        self.fps_limit = fps_limit
        self.clock = pygame.time.Clock()
        self.delta = 0
        self.screen_dim = screen_dimension
        self.resources_path = resources_root_path
        self.key_ups = []
        self.key_downs = []
        self.mouse_ups: list[bool, bool, bool] = [False, False, False]
        self.mouse_downs: list[bool, bool, bool] = [False, False, False]
        self.camera_pos: pygame.Vector2 = camera_pos
        self.game_objects: OrderedDict[str, util.GameObject] = OrderedDict()
        self.collidable_objects: list[util.GameObject] = []
        self.global_fonts: dict[str, pygame.font.Font] = {}
        self.object_collision_rects: list[pygame.Rect] = []

    def mainloop(self):
        done = False

        self.delta = 0
        while not done:
            self.object_collision_rects.clear()
            t = pygame.time.get_ticks()
            self.key_ups.clear()
            self.key_downs.clear()
            self.mouse_ups = [False, False, False]
            self.mouse_downs = [False, False, False]
            # ___START___
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

            for gm in self.game_objects.values():
                gm.early_update()

            # ___MAIN UPDATE___
            for gm in self.game_objects.values():
                gm.update()
            # _________________

            # __ BLIT THINGS ON THE SCREEN __
            self.display.fill(self.background)
            for gm in self.game_objects.values():
                gm.blit(self.display)
            pygame.display.update()
            self.delta = (pygame.time.get_ticks() - t) / 1000
            self.clock.tick(self.fps_limit)

    def add_gameObject(self, gameObject: util.GameObject) -> None:
        self.game_objects.setdefault(gameObject.name, gameObject)

    def add_collidable_object(self, gameObject: util.GameObject) -> None:
        self.collidable_objects.append(gameObject)

    def is_colliding(self, rect: pygame.Rect, exclude: Optional[str] = None) -> int:
        if len(self.object_collision_rects) == 0:
            self.object_collision_rects = list(map(lambda obj: obj.get_collision_rect(), self.collidable_objects))
        il = rect.collidelistall(self.object_collision_rects)
        for i in il:
            if i > len(self.collidable_objects) - 1:
                continue
            if self.collidable_objects[i].name != exclude:
                return i
        return -1

    def remove_collidable_object(self, obj: util.GameObject) -> bool:
        for i, o in enumerate(self.collidable_objects):
            if o == obj:
                self.collidable_objects.pop(i)
                return True
        return False
