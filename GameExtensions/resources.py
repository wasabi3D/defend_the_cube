from GameManager.util import GameObject
from GameManager.resources import load_img
from GameExtensions.util import ShakeGenerator
import GameManager.singleton as sing
from pygame.math import Vector2
import pygame
from random import randint, choice
from random import random
from abc import ABCMeta, abstractmethod


class Resource(metaclass=ABCMeta):
    """
    Classe qui représente tous les ressources dont on peut les miner.
    """

    @abstractmethod
    def mine(self):
        """
        Fonction qui doit être appellée quand un joueur mine un objet ressource.
        """
        pass


class Tree(GameObject, Resource):
    """
    Arbre.
    """
    def __init__(self, pos: Vector2, name: str, size_min=64, size_max=96, apple_probability=0.1):
        """
        :param pos: La position initiale de l'objet. La valeur par défaut est pygame.Vector2(0, 0).
        :param name: Le nom de l'objet.
        """
        size = randint(size_min, size_max)
        self.has_apple = random() <= apple_probability
        if self.has_apple:
            img = load_img("resources/environment/tree_with_apple.png", (size, size))
        else:
            img = load_img("resources/environment/tree.png", (size, size))
        super().__init__(pos, 0, img, name)
        self.rect_surf = pygame.Surface((size * 0.4, size * 0.4))
        self.col_offset = Vector2(0, 20)
        self.shake = ShakeGenerator(15, -22, 13, 23, 0, 0.1, 0.9, 0.86)

    def get_collision_rect(self) -> pygame.Rect:
        """
        Permet d'obtenir le hitbox de l'arbre.
        :return: Le hitbox de type pygame.Rect
        """
        return self.rect_surf.get_rect(center=self.get_real_pos() + self.col_offset)

    def get_screen_pos(self) -> Vector2:
        p = super().get_screen_pos()
        sh = self.shake.get_shake()
        p += sh
        self.shake.next_frame(sing.ROOT.delta)
        return p

    def mine(self):
        self.shake.y_intensity *= -1 if random() > 0.5 else 1
        self.shake.begin(0)


class Rock(GameObject, Resource):
    """
    Roche.
    """

    def __init__(self, pos: Vector2, name: str, size_min=48, size_max=64):
        """
        :param pos: La position initiale de l'objet. La valeur par défaut est pygame.Vector2(0, 0).
        :param name: Le nom de l'objet.
        """
        size = randint(size_min, size_max)
        img = ["rock.png", "rock2.png"]
        super().__init__(pos, 0, load_img(f"resources/environment/{choice(img)}", (size, size)), name)
        self.rect_surf = pygame.Surface((size * 0.6, size * 0.4))
        self.col_offset = Vector2(0, 15)
        self.shake = ShakeGenerator(11, 8, 13, 17, 0, 0, 0.9, 0.9)

    def get_collision_rect(self) -> pygame.Rect:
        """
        Permet d'obtenir le hitbox de la roche.
        :return: Le hitbox de type pygame.Rect
        """
        return self.rect_surf.get_rect(center=self.get_real_pos() + self.col_offset)

    def get_screen_pos(self) -> Vector2:
        p = super().get_screen_pos()
        sh = self.shake.get_shake()
        p += sh
        self.shake.next_frame(sing.ROOT.delta)
        return p

    def mine(self):
        self.shake.begin(0)
