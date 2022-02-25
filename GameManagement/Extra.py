import GameManagement.Utilities.Objects as Obj
import GameManagement.Utilities.Components as Comp
import GameManagement.singleton as sing
import pygame
import math


class Camera(Obj.GameObject):
    def __init__(self, pos: pygame.Vector2, rotation: float):
        super().__init__(pos, rotation, pygame.Vector2(1, 1), pygame.Surface(sing.ROOT.screen_dim),
                         [Comp.CameraComponent()])