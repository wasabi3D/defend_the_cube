from GameManager.util import GameObject
from GameManager.resources import load_img
import pygame
from pygame.locals import *
import GameManager.singleton as sing
from pygame.math import Vector2


class Player(GameObject):
    SPEED = 250

    def __init__(self, pos: Vector2, rotation: float, name: str):
        self.original = load_img("resources/player/tmp_player.png", (40, 40))
        super().__init__(pos, rotation, self.original.copy(), name)
        self.right_oriented = True

    def update(self) -> None:
        pressed = pygame.key.get_pressed()
        dx, dy = 0, 0
        if pressed[K_UP]:
            dy += -1
        if pressed[K_DOWN]:
            dy += 1
        if pressed[K_RIGHT]:
            if not self.right_oriented:
                self.image = self.original.copy()
            self.right_oriented = True
            dx += 1
        if pressed[K_LEFT]:
            if self.right_oriented:
                self.image = pygame.transform.flip(self.original.copy(), True, False)
            self.right_oriented = False
            dx += -1

        # Check for collisions  https://youtu.be/m7GnJo_oZUU
        rp = self.get_real_pos()
        dx_tmp_rect = self.image.get_rect(center=rp + Vector2(dx, 0))
        dy_tmp_rect = self.image.get_rect(center=rp + Vector2(0, dy))
        obj_lst = tuple(map(lambda obj: obj.get_collision_rect(), sing.ROOT.collidable_objects))
        # print(obj_lst)
        # print(f"Player {dx_tmp_rect}")
        if dx_tmp_rect.collidelist(obj_lst) != -1:
            dx = 0
        if dy_tmp_rect.collidelist(obj_lst) != -1:
            dy = 0

        mov = Vector2(dx, dy)
        if mov.length_squared() != 0:
            self.translate(mov.normalize() * sing.ROOT.delta * Player.SPEED)
            sing.ROOT.camera_pos = self.get_real_pos().copy()
        print(sing.ROOT.delta)
        super().update()
