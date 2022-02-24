import GameManagement.Utilities.Objects as Obj
import GameManagement.Utilities.Components as Comp
import GameManagement.singleton as sing
import pygame
import math


class Camera(Obj.GameObject):
    def __init__(self, pos: pygame.Vector2, rotation: float):
        super().__init__(pos, rotation, pygame.Vector2(1, 1), pygame.Surface(sing.ROOT.screen_dim),
                         [Comp.CameraComponent()])
        self.mov = pygame.Vector2(1, 0) # test

    def normal_update(self, scene) -> None:
        """
        This is just a test method. Will be removed in the future.
        :param scene:
        :return:
        """
        self.rotate(math.pi / 480)
        if self.pos.x > 50 or self.pos.x < -50:
            self.mov.x *= -1

        self.translate(self.mov, True)
        super().normal_update(scene)

