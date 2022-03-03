from GameManager.util import GameObject
from GameManager.resources import load_img
import pygame
from pygame.locals import *
import GameManager.singleton as sing
from pygame.math import Vector2


class Player(GameObject):
    SPEED = 100

    def __init__(self, pos: Vector2, rotation: float, name: str):
        self.original = load_img("resources/player/tmp_player.png", (48, 48))
        super().__init__(pos, rotation, self.original.copy(), name)
        self.right_oriented = True

    def update(self) -> None:
        pressed = pygame.key.get_pressed()
        mov = Vector2(0, 0)
        if pressed[K_UP]:
            mov += Vector2(0, -1)
        if pressed[K_DOWN]:
            mov += Vector2(0, 1)
        if pressed[K_RIGHT]:
            if not self.right_oriented:
                self.image = self.original.copy()
            self.right_oriented = True
            mov += Vector2(1, 0)
        if pressed[K_LEFT]:
            if self.right_oriented:
                self.image = pygame.transform.flip(self.original.copy(), True, False)
            self.right_oriented = False
            mov += Vector2(-1, 0)

        if mov.length_squared() != 0:
            self.translate(mov.normalize() * sing.ROOT.delta * Player.SPEED)
            sing.ROOT.camera_pos = self.get_real_pos().copy()
        print(sing.ROOT.delta)
        super().update()
