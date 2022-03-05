from GameManager.util import GameObject
from GameManager.resources import load_img
from GameExtensions.util import ShakeGenerator
import GameManager.singleton as sing
from pygame.math import Vector2
import pygame
from random import randint


class Resource:
    """
    Classe qui représente tous les ressources dont on peut les miner.
    """

    def mine(self):
        """
        Fonction qui doit être appellée quand un joueur mine un objet ressource.
        """
        pass


class Tree(GameObject, Resource):
    """
    Arbre.
    """
    def __init__(self, pos: Vector2, name: str, size_min=96, size_max=128):
        """
        :param pos: La position initiale de l'objet. La valeur par défaut est pygame.Vector2(0, 0).
        :param name: Le nom de l'objet.
        """
        size = randint(size_min, size_max)
        super().__init__(pos, 0, load_img("resources/environment/tree.png", (size, size)), name)
        self.rect_surf = pygame.Surface((size * 0.4, size * 0.4))
        self.col_offset = Vector2(0, 30)
        self.shake = ShakeGenerator(11, 8, 13, 17, 0, 0, 0.9, 0.9)

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
        self.shake.begin(0)
