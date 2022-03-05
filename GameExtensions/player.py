from GameManager.util import GameObject
from GameManager.resources import load_img
from GameExtensions.resources import Resource
from GameManager.locals import MOUSE_LEFT
import pygame
from pygame.locals import *
import GameManager.singleton as sing
from pygame.math import Vector2


class Player(GameObject):
    SPEED = 210
    RIGHT = "right"
    LEFT = "left"
    UP = "up"
    DOWN = "down"

    def __init__(self, pos: Vector2, rotation: float, name: str):
        self.original = load_img("resources/player/tmp_player.png", (40, 40))
        super().__init__(pos, rotation, self.original.copy(), name)
        self.right_oriented = True
        self.punch_hitbox = pygame.Surface((15, 15))
        self.facing = Player.RIGHT

    def update(self) -> None:
        # MOVEMENT
        pressed = pygame.key.get_pressed()
        dx, dy = 0, 0
        if pressed[K_UP]:
            dy += -1
            self.facing = Player.UP
        if pressed[K_DOWN]:
            dy += 1
            self.facing = Player.DOWN
        if pressed[K_RIGHT]:
            if not self.right_oriented:
                self.image = self.original.copy()
            self.right_oriented = True
            dx += 1
            self.facing = Player.RIGHT
        if pressed[K_LEFT]:
            if self.right_oriented:
                self.image = pygame.transform.flip(self.original.copy(), True, False)
            self.right_oriented = False
            dx += -1
            self.facing = Player.LEFT

        # Check for collisions  https://youtu.be/m7GnJo_oZUU
        rp = self.get_real_pos()
        dx_tmp_rect = self.image.get_rect(center=rp + Vector2(dx, 0))
        dy_tmp_rect = self.image.get_rect(center=rp + Vector2(0, dy))
        if sing.ROOT.is_colliding(dx_tmp_rect) != -1:
            dx = 0
        if sing.ROOT.is_colliding(dy_tmp_rect) != -1:
            dy = 0

        mov = Vector2(dx, dy)
        if mov.length_squared() != 0:
            self.translate(mov.normalize() * sing.ROOT.delta * Player.SPEED)
            sing.ROOT.camera_pos = self.get_real_pos().copy()

        # PUNCH
        if sing.ROOT.mouse_downs[MOUSE_LEFT]:
            ph = self.generate_punch_hitbox()
            hit = sing.ROOT.is_colliding(ph)
            if hit != -1:
                obj = sing.ROOT.collidable_objects[hit]
                if isinstance(obj, Resource):
                    obj.mine()

        super().update()

    def generate_punch_hitbox(self) -> pygame.Rect:
        p = self.get_real_pos()
        if self.facing == Player.RIGHT:
            return self.punch_hitbox.get_rect(center=p + Vector2(20, 0))
        elif self.facing == Player.LEFT:
            return self.punch_hitbox.get_rect(center=p + Vector2(-20, 0))
        elif self.facing == Player.UP:
            return self.punch_hitbox.get_rect(center=p + Vector2(0, -20))
        elif self.facing == Player.DOWN:
            return self.punch_hitbox.get_rect(center=p + Vector2(0, 20))
