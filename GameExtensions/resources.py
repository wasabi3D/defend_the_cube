from GameManager.funcs import resize_surface
from GameManager.resources import load_sound

from GameExtensions.util import ShakeGenerator
from GameExtensions.items import *
from GameExtensions.locals import ITEM_FONT_NAME

from pygame.math import Vector2
import pygame

from random import randint, choice
from random import random

from abc import ABCMeta, abstractmethod


class Resource(GameObject, metaclass=ABCMeta):
    """
    Classe qui représente tous les ressources dont on peut les miner.
    """
    def __init__(self, pos: Vector2,
                 name: str,
                 original_img: pygame.Surface,
                 hitbox_rect: pygame.Surface,
                 hitbox_offset: pygame.Vector2,
                 shake_gen: ShakeGenerator,
                 size_decrease_rate=0.9,
                 destroy_threshold=0.25):
        super().__init__(pos, 0, original_img, name)
        self.clone_img = original_img.copy()
        self.rect_surf = hitbox_rect
        self.rect_surf_clone = hitbox_rect.copy()
        self.col_offset = hitbox_offset
        self.size = 1
        self.decrease_rate = size_decrease_rate
        self.shake = shake_gen
        self.destroy_threshold = destroy_threshold

    def get_collision_rect(self) -> pygame.Rect:
        """
        Permet d'obtenir le hitbox de l'arbre.
        :return: Le hitbox de type pygame.Rect
        """
        return self.rect_surf.get_rect(center=self.get_real_pos() + self.col_offset)

    def get_screen_pos(self) -> Vector2:
        p = super().get_screen_pos()
        p += self.shake.get_shake()
        self.shake.next_frame(sing.ROOT.delta)
        return p

    @abstractmethod
    def on_mine(self):
        """
        Fonction qui doit être appellée quand un joueur mine un objet ressource.
        """
        self.size *= self.decrease_rate
        self.image = resize_surface(self.clone_img, self.size)
        self.rect_surf = resize_surface(self.rect_surf_clone, self.size)


class Tree(Resource):
    """
    Arbre.
    """

    APPLE_PROBABILITY = 0.4

    def __init__(self, pos: Vector2, name: str, size_min=64, size_max=96, apple_probability=0.1):
        """
        :param pos: La position initiale de l'objet. La valeur par défaut est pygame.Vector2(0, 0).
        :param name: Le nom de l'objet.
        """
        size = randint(size_min, size_max)
        self.has_apple = random() <= apple_probability
        if self.has_apple:
            img = load_img("resources/environment/tree_topdown_with_apple.png", (size, size))
        else:
            img = load_img("resources/environment/tree_topdown.png", (size, size))
        super().__init__(pos, name, img, pygame.Surface((size * 0.4, size * 0.4)), Vector2(0, 20),
                         ShakeGenerator(15, -22, 13, 23, 0, 0.1, 0.9, 0.86))
        self.log_item = Log(1, sing.ROOT.global_fonts[ITEM_FONT_NAME])
        load_sound("resources/sounds/wood_farm.wav", "wood_farm")

    def on_mine(self):
        super().on_mine()
        inventory = sing.ROOT.game_objects["inventory"]
        inventory.add_obj_ins(self.log_item.copy())
        self.shake.y_intensity *= -1 if random() > 0.5 else 1
        self.shake.begin(0)
        sing.ROOT.sounds["wood_farm"].play()
        if self.has_apple and random() <= Tree.APPLE_PROBABILITY:
            inventory.add_obj_ins(Apple(1, sing.ROOT.global_fonts[ITEM_FONT_NAME]))


class Rock(Resource):
    """
    Roche.
    """
    def __init__(self, pos: Vector2, name: str, size_min=48, size_max=64):
        """
        :param pos: La position initiale de l'objet. La valeur par défaut est pygame.Vector2(0, 0).
        :param name: Le nom de l'objet.
        """
        size = randint(size_min, size_max)
        img = ["rock_topdown.png"]
        super().__init__(pos, name, load_img(f"resources/environment/{choice(img)}", (size, size)),
                         pygame.Surface((size * 0.6, size * 0.4)), Vector2(0, 15),
                         ShakeGenerator(11, 8, 13, 17, 0, 0, 0.9, 0.9))
        load_sound("resources/sounds/rock_farm.wav", "rock_farm")
        self.stone_item = Stone(1, sing.ROOT.global_fonts[ITEM_FONT_NAME])

    def on_mine(self):
        super().on_mine()

        inventory = sing.ROOT.game_objects["inventory"]
        inventory.add_obj_ins(self.stone_item.copy())
        if random() <= 0.14:
            inventory.add_obj_ins(IronOre(randint(1, 2), sing.ROOT.global_fonts[ITEM_FONT_NAME]))
        self.shake.begin(0)
        sing.ROOT.sounds["rock_farm"].play()
