from GameManager.util import GameObject
from GameManager.resources import load_img
from GameManager.locals import MOUSE_LEFT
from GameManager.funcs import tuple2Vec2
import GameManager.singleton as sing

from GameExtensions.util import Animation, Animator, MovementGenerator, Entity
from GameExtensions.resources import Resource
from GameExtensions.inventory import Inventory
from GameExtensions.locals import *
from GameExtensions.items import Weapon
from GameExtensions.enemy import Enemy

import pygame
from pygame.locals import *
from pygame.math import Vector2

import math


class Slash(GameObject):
    """
    La classe pour l'animation des slash quand le joueur utilise une épée
    """
    def __init__(self, pos: Vector2):
        super().__init__(pos, math.pi / 2, load_img("resources/anim/slash/5.png"), "slash")
        self.animator = Animator()

        b = "resources/anim/slash/"
        self.animator.register_anim("slash", Animation(Animator.load_frames_by_pattern(b, ".png", 0, 9), 0.015, "calm"))
        self.animator.register_anim("calm", Animation([load_img("resources/blank.png")], 1))
        self.animator.start_anim("calm")

    def slash(self) -> None:
        """
        Commence l'animation
        """
        self.animator.start_anim("slash")

    def update(self) -> None:
        self.animator.update(sing.ROOT.delta)
        self.image = self.animator.get_cur_frame(rotation=self.parent.rotation - math.pi / 2)


class Hands(GameObject):
    """
    La classe pour les 2 mains du joueur
    """
    DEFAULT_Y = 12
    ANIM_TIME = 0.15
    SWORD_ANIM_TIME = 0.2
    ANIM_DIST = 15

    def __init__(self, pos: Vector2):
        """

        :param pos: La position des mains
        """
        super().__init__(pos, 0, pygame.Surface((0, 0)), "hands")
        hand_img = load_img("resources/player/hand.png", (10, 10))
        self.children.add_gameobject(GameObject(Vector2(0, Hands.DEFAULT_Y), 0, hand_img, "right_hand"))
        self.children.add_gameobject(GameObject(Vector2(0, -Hands.DEFAULT_Y), 0, hand_img, "left_hand"))
        self.children["right_hand"].children.add_gameobject(GameObject(Vector2(0, 0), 0, pygame.Surface((0, 0)), "item"))
        self.fw = True  # si la main droite avance ou pas
        self.sword_mode = False
        self.time_remain = 0
        self.distance_from_parent = Vector2(0, 0).distance_to(self.pos + self.children["right_hand"].pos)
        self.x_dist_from_parent = self.pos.x + self.children["right_hand"].pos.x

    def update(self):
        if self.time_remain > 0:
            self.time_remain -= sing.ROOT.delta
            d = Hands.ANIM_DIST / Hands.ANIM_TIME

            if self.sword_mode:
                time = Hands.SWORD_ANIM_TIME
                angle = (math.pi / 2) * (((time - self.time_remain) / time)) - (math.pi / 2) * 1
                x = math.cos(angle) * self.distance_from_parent
                y = math.sin(angle) * self.distance_from_parent
                self.children["right_hand"].translate(Vector2(x, -y) - Vector2(self.x_dist_from_parent, 0), False)
            else:
                self.children["right_hand"].translate(Vector2(d * (1 if self.fw else -1) * sing.ROOT.delta, 0))
                self.children["left_hand"].translate(Vector2(d * (-1 if self.fw else 1) * sing.ROOT.delta, 0))
        else:
            if self.sword_mode:
                self.fw = False
                self.children["right_hand"].translate(Vector2(0, Hands.DEFAULT_Y), False)
                self.children["left_hand"].translate(Vector2(0, -Hands.DEFAULT_Y), False)
            else:
                if self.fw:
                    self.fw = False
                    self.time_remain = Hands.ANIM_TIME / 2
                    self.children["right_hand"].translate(Vector2(Hands.ANIM_DIST, Hands.DEFAULT_Y), False)
                    self.children["left_hand"].translate(Vector2(-Hands.ANIM_DIST, -Hands.DEFAULT_Y), False)
                else:
                    self.children["right_hand"].translate(Vector2(0, Hands.DEFAULT_Y), False)
                    self.children["left_hand"].translate(Vector2(0, -Hands.DEFAULT_Y), False)

    def punch(self, sword_mode=False):
        """
        Déclanche l'animation d'un coup de poing
        :param sword_mode: Si on utilise l'animation pour l'épée ou pas
        """
        self.sword_mode = sword_mode
        self.fw = True
        self.time_remain = Hands.SWORD_ANIM_TIME if sword_mode else Hands.ANIM_TIME / 2


class Player(Entity):
    """
    Classe qui définit le joueur.
    """
    SPEED = 220
    DECEL_WHEN_HOLDING = 0.4
    DECEL_SHIFT = 0.6
    RIGHT = "right"
    LEFT = "left"
    UP = "up"
    DOWN = "down"
    SPRITE_SIZE = (32, 32)
    HAND_OFFSET = Vector2(15, -5)
    HITBOX_SIZE = (26, 26)
    MAX_HP = 100

    def __init__(self, pos: Vector2, rotation: float, name: str):
        """

        :param pos: La position initiale.
        :param rotation: La rotation initiale.
        :param name: Le nom du joueur.
        """
        super().__init__(pos, rotation, load_img("resources/player/topdown/player_east.png", Player.SPRITE_SIZE), name,
                         Player.MAX_HP, Player.MAX_HP, pygame.Surface(Player.HITBOX_SIZE))
        self.mov_gen.kb_decay = 0.08
        self.punch_hitbox = pygame.Surface((15, 15))
        # self.player_hitbox = pygame.Surface(Player.HITBOX_SIZE)
        self.facing = Player.RIGHT
        self.children.add_gameobject(GameObject(Vector2(0, 0), 0, pygame.Surface((0, 0)), "item_holder"))
        self.children.add_gameobject(Hands(Vector2(18, 0)))
        self.children.add_gameobject(Slash(Vector2(35, 10)))
        self.inventory: Inventory = sing.ROOT.game_objects["inventory"]
        if not isinstance(self.inventory, Inventory):
            raise TypeError("Not an instance of Inventory")

        self.last_hold = ""

    def update(self) -> None:
        super().update()
        # MOVEMENT
        pressed = pygame.key.get_pressed()
        dx, dy = 0, 0
        if pressed[K_w]:
            if self.facing != Player.UP:
                self.rotate(math.pi / 2, False)
            dy += -1
            self.facing = Player.UP
        if pressed[K_s]:
            if self.facing != Player.DOWN:
                self.rotate(3 * math.pi / 2, False)
            dy += 1
            self.facing = Player.DOWN
        if pressed[K_d]:
            if self.facing != Player.RIGHT:
                self.rotate(0, False)
            dx += 1
            self.facing = Player.RIGHT
        if pressed[K_a]:
            if self.facing != Player.LEFT:
                self.rotate(math.pi, False)
            dx += -1
            self.facing = Player.LEFT

        # Calcul du vecteur mouvement final
        mov = Vector2(dx, dy)  # l'input du joueur
        if mov.length_squared() != 0:
            mov.normalize_ip()
            mov *= sing.ROOT.delta * Player.SPEED
            if len(self.children["item_holder"].children) > 0 and \
                    PLACEABLE in self.children["item_holder"].children["item"].tags:
                mov *= Player.DECEL_WHEN_HOLDING
            if pressed[K_LSHIFT]:
                mov *= Player.DECEL_SHIFT

        self.translate(self.mov_gen.move(mov.x, mov.y))
        sing.ROOT.camera_pos = self.get_real_pos().copy()

        # Affichage de l'item que le joueur selectionne
        selected = self.inventory.hotbar[self.inventory.selected]
        if selected.name != self.last_hold:
            self.last_hold = selected.name
            self.children["item_holder"].children.clear()

            self.children["hands"].children["right_hand"].children.clear()

            if HOLDABLE in selected.tag:
                img = selected.img.copy()
                self.children["item_holder"].children.add_gameobject(GameObject(Vector2(32, 0), 0, img, "item",
                                                                                tags=selected.tag))
            else:
                new_img = pygame.Surface((0, 0)) if selected.name == 'empty' else pygame.transform.scale(selected.img,
                                                                                                         (12, 12))
                self.children["hands"].children["right_hand"].children.add_gameobject(
                    GameObject(Vector2(2, -6), 0, new_img, "item"))

        # Click gauche
        if sing.ROOT.mouse_downs[MOUSE_LEFT]:
            if SLASHABLE in selected.tag:
                self.children["hands"].punch(sword_mode=True)
                self.children["slash"].slash()
            elif HOLDABLE not in selected.tag and DONT_SLASH not in selected.tag:
                self.children["hands"].punch(sword_mode=False)

            ph = self.generate_punch_hitbox()
            if isinstance(selected, Weapon):
                hits = sing.ROOT.collide_all(ph)
                for i in hits:
                    obj = sing.ROOT.collidable_objects[i]
                    if isinstance(obj, Resource):
                        obj.on_mine()
                    elif isinstance(obj, Enemy):
                        vec = (obj.get_real_pos() - self.get_real_pos()).normalize()
                        obj.get_damage(10, vec * 1000)
            else:
                hit = sing.ROOT.is_colliding(ph)
                if hit != -1:
                    obj = sing.ROOT.collidable_objects[hit]
                    if isinstance(obj, Resource):
                        obj.on_mine()

        # Mise a jour de la barre en bas qui indique la vie
        hpb = sing.ROOT.game_objects["HPBar"]
        hpb.prop = self.hp / Player.MAX_HP

        super().update()

    def generate_punch_hitbox(self) -> pygame.Rect:
        """
        Fonction qui permet de calculer la partie punchée par le joueur en fonction de la position et la rotation.

        :return: Un rectangle de type pygame.Rect
        """
        p = self.get_real_pos()
        if self.facing == Player.RIGHT:
            return self.punch_hitbox.get_rect(center=p + Vector2(20, 0))
        elif self.facing == Player.LEFT:
            return self.punch_hitbox.get_rect(center=p + Vector2(-20, 0))
        elif self.facing == Player.UP:
            return self.punch_hitbox.get_rect(center=p + Vector2(0, -20))
        elif self.facing == Player.DOWN:
            return self.punch_hitbox.get_rect(center=p + Vector2(0, 20))

    def get_direction_vec(self) -> Vector2:
        """
        Calcule un vecteur normalisé qui représente la rotation du joueur

        :return: Un Vector2
        """
        x = math.cos(self.rotation)
        y = -math.sin(self.rotation)
        return Vector2(x, y).normalize()

    def blit(self, screen: pygame.Surface, apply_alpha=True) -> None:
        screen.blit(self.image, self.image.get_rect(center=tuple2Vec2(sing.ROOT.screen_dim) / 2))
        super().blit_children(screen, apply_alpha)
