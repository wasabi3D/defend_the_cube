from GameManager.util import GameObject
from GameManager.resources import load_img
from GameExtensions.resources import Resource
from GameExtensions.util import Animation, Animator
from GameManager.locals import MOUSE_LEFT
import pygame
from pygame.locals import *
import GameManager.singleton as sing
from pygame.math import Vector2
from GameManager.funcs import tuple2Vec2


class Player(GameObject):
    SPEED = 210
    RIGHT = "right"
    LEFT = "left"
    UP = "up"
    DOWN = "down"
    SPRITE_SIZE = (48, 48)

    def __init__(self, pos: Vector2, rotation: float, name: str):
        super().__init__(pos, rotation, pygame.Surface(Player.SPRITE_SIZE), name)
        self.right_oriented = True
        self.punch_hitbox = pygame.Surface((15, 15))
        self.facing = Player.RIGHT
        self.idle = True
        self.animator = Animator()
        right_idle = Animation(Animator.load_frames_by_pattern("resources/player/anim/idle/player_idle_", ".png",
                                                               1, 4, override_size=Player.SPRITE_SIZE), 0.3)
        left_idle = Animation(Animator.load_frames_by_pattern("resources/player/anim/idle/player_idle_", ".png",
                                                              1, 4,
                                                              conv=lambda s: pygame.transform.flip(s, True, False),
                                                              override_size=Player.SPRITE_SIZE), 0.3)
        running_right = Animation([load_img("resources/player/tmp_player.png", Player.SPRITE_SIZE)], 0.3)
        running_left = Animation(
            [pygame.transform.flip(load_img("resources/player/tmp_player.png", Player.SPRITE_SIZE), True, False)], 0.3)

        front_idle = Animation(Animator.load_frames_by_pattern("resources/player/anim/idle/front/", ".png",
                                                               1, 6, override_size=Player.SPRITE_SIZE), 0.4)

        self.animator.register_anim("right_idle", right_idle)
        self.animator.register_anim("left_idle", left_idle)
        self.animator.register_anim("running_right", running_right)
        self.animator.register_anim("running_left", running_left)
        self.animator.register_anim("front_idle", front_idle)
        self.animator.start_anim("front_idle")

    def update(self) -> None:
        self.animator.update(sing.ROOT.delta)

        # MOVEMENT
        pressed = pygame.key.get_pressed()
        dx, dy = 0, 0
        prev_idle = self.idle
        self.idle = True
        if pressed[K_UP]:
            self.idle = False
            dy += -1
            self.facing = Player.UP
        if pressed[K_DOWN]:
            self.idle = False
            dy += 1
            self.facing = Player.DOWN
        if pressed[K_RIGHT]:
            self.idle = False
            if not self.right_oriented or not prev_idle:
                self.animator.start_anim("running_right")
            self.right_oriented = True
            dx += 1
            self.facing = Player.RIGHT
        if pressed[K_LEFT]:
            self.idle = False
            if self.right_oriented or not prev_idle:
                self.animator.start_anim("running_left")
            self.right_oriented = False
            dx += -1
            self.facing = Player.LEFT

        if not prev_idle and self.idle:
            self.animator.start_anim("right_idle" if self.right_oriented else "left_idle")

        self.image = self.animator.get_cur_frame()

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
                    obj.on_mine()

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

    def blit(self, screen: pygame.Surface, apply_alpha=True) -> None:
        screen.blit(self.image, self.image.get_rect(center=tuple2Vec2(sing.ROOT.screen_dim) / 2))
        super().blit_children(screen, apply_alpha)
