import GameManagement.SceneManager
import GameManagement.Utilities.Objects as Obj
import GameManagement.singleton as sing
import GameManagement.UI.base as base
from GameManagement.Utilities.funcs import is_included, tuple2Vec2
import pygame
import typing


class UIEventHandler(Obj.GameObject):
    def __init__(self, components: list):
        super().__init__(pygame.Vector2(0, 0), 0, pygame.Vector2(1, 1), pygame.Surface((0, 0)), components)
        self.check_objects: list[base.BaseUIObject] = []

    def get_real_pos(self) -> pygame.Vector2:
        return pygame.Vector2(0, 0)

    def blit(self, screen: pygame.Surface, camera_pos_modifier: pygame.Vector2) -> None:
        return

    def early_update(self, scene: GameManagement.SceneManager.Scene) -> None:
        for btn in range(0, 3):
            if not sing.ROOT.mouse_downs[btn]:
                continue

            for obj in self.check_objects:
                if is_included(tuple2Vec2(pygame.mouse.get_pos()), obj.image.get_rect(center=obj.get_screen_pos())):

                    obj.on_mouse_click_down(scene, tuple2Vec2(pygame.mouse.get_pos()), btn)

