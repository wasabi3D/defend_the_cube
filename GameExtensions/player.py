from GameManager.util import GameObject
from GameManager.resources import load_img
from GameManager.locals import MOUSE_LEFT
from GameManager.funcs import tuple2Vec2
import GameManager.singleton as sing

from GameExtensions.util import Animation, Animator, MovementGenerator
from GameExtensions.resources import Resource
from GameExtensions.inventory import Inventory
from GameExtensions.locals import HOLDABLE, PLACEABLE

import pygame
from pygame.locals import *
from pygame.math import Vector2

import math


class Hand(GameObject):
    HAND_SIZE = (8, 8)

    def __init__(self, pos: Vector2, rotation: float):
        super().__init__(pos, rotation, load_img("resources/player/hand.png", Hand.HAND_SIZE), "hand")


class Player(GameObject):
    SPEED = 300
    DECEL_WHEN_HOLDING = 0.4
    DECEL_SHIFT = 0.6
    RIGHT = "right"
    LEFT = "left"
    UP = "up"
    DOWN = "down"
    SPRITE_SIZE = (32, 32)
    HAND_OFFSET = Vector2(15, -5)
    HITBOX_SIZE = (26, 26)

    def __init__(self, pos: Vector2, rotation: float, name: str):
        super().__init__(pos, rotation, load_img("resources/player/body.png", Player.SPRITE_SIZE), name)
        self.punch_hitbox = pygame.Surface((15, 15))
        self.player_hitbox = pygame.Surface(Player.HITBOX_SIZE)
        self.facing = Player.RIGHT
        self.animator = Animator()
        base = "resources/player/topdown/"
        self.animator.register_anim("north", Animation([load_img(base + "player_north.png")], 1))
        self.animator.register_anim("south", Animation([load_img(base + "player_south.png")], 1))
        self.animator.register_anim("west", Animation([load_img(base + "player_west.png")], 1))
        self.animator.register_anim("east", Animation([load_img(base + "player_east.png")], 1))
        self.animator.start_anim("east")
        self.children.add_gameobject(GameObject(Vector2(0, 0), 0, pygame.Surface((0, 0)), "item_holder"))
        self.inventory: Inventory = sing.ROOT.game_objects["inventory"]
        self.movment = MovementGenerator(self.player_hitbox, self)
        if not isinstance(self.inventory, Inventory):
            raise TypeError("Not an instance of Inventory")

        self.last_hold = ""

    def update(self) -> None:
        self.animator.update(sing.ROOT.delta)

        # MOVEMENT
        pressed = pygame.key.get_pressed()
        dx, dy = 0, 0
        if pressed[K_w]:
            if self.facing != Player.UP:
                self.animator.start_anim("north")
                self.children["item_holder"].rotate(math.pi / 2, False)
            dy += -1
            self.facing = Player.UP
        if pressed[K_s]:
            if self.facing != Player.DOWN:
                self.animator.start_anim("south")
                self.children["item_holder"].rotate(3 * math.pi / 2, False)
            dy += 1
            self.facing = Player.DOWN
        if pressed[K_d]:
            if self.facing != Player.RIGHT:
                self.animator.start_anim("east")
                self.children["item_holder"].rotate(0, False)
            dx += 1
            self.facing = Player.RIGHT
        if pressed[K_a]:
            if self.facing != Player.LEFT:
                self.animator.start_anim("west")
                self.children["item_holder"].rotate(math.pi, False)
            dx += -1
            self.facing = Player.LEFT

        self.image = self.animator.get_cur_frame()

        mov = Vector2(dx, dy)
        if mov.length_squared() != 0:
            mov.normalize_ip()
            mov *= sing.ROOT.delta * Player.SPEED
            if len(self.children["item_holder"].children) > 0 and \
                    PLACEABLE in self.children["item_holder"].children["item"].tags:
                mov *= Player.DECEL_WHEN_HOLDING
            if pressed[K_LSHIFT]:
                mov *= Player.DECEL_SHIFT
            mov = self.movment.move(mov.x, mov.y)
            self.translate(mov)
            sing.ROOT.camera_pos = self.get_real_pos().copy()
            
        # PUNCH
        if sing.ROOT.mouse_downs[MOUSE_LEFT]:
            ph = self.generate_punch_hitbox()
            hit = sing.ROOT.is_colliding(ph)
            if hit != -1:
                obj = sing.ROOT.collidable_objects[hit]
                if isinstance(obj, Resource):
                    obj.on_mine()

        selected = self.inventory.hotbar[self.inventory.selected]
        if selected.name != self.last_hold:
            self.last_hold = selected.name
            self.children["item_holder"].children.clear()
            if HOLDABLE in selected.tag:
                img = selected.img.copy()
                self.children["item_holder"].children.add_gameobject(GameObject(Vector2(32, 0), 0, img, "item",
                                                                                tags=selected.tag))

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
