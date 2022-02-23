import pygame
from pygame.sprite import Sprite
from pygame.math import Vector2
from typing import Union
from GameManagement.locals import *
import math


def rad2deg(radian: float) -> float:
    """
    Convertit l'angle en radian en degré

    :param radian: L'angle qu'on veut convertir en radian
    :return: 180 * (radian / pi )
    """
    return RAD2DEG * radian


class BaseObject:
    """
    Définit la base de tous les objets du jeu(camera inclu).
    """
    def __init__(self, pos: Vector2, rotation: float, object_scale: Vector2):
        """

        :param pos: La position initiale de l'objet. La valeur par défaut est pygame.Vector2(0, 0).
        :param rotation: La rotation en radian initiale de l'objet. La valeur par défaut est 0.
        :param object_scale: L'échelle initiale de l'objet. La valeur par défaut est pygame.Vector2(1, 1).
        """
        self.pos: Vector2 = pos  # Position du centre de l'image et non topleft
        self.rotation = rotation
        self.scale = object_scale

    def translate(self, movement: Vector2, additive=True) -> None:
        """
        Fonction qui permet de modifier la position de l'objet.

        :param movement: Un vecteur qui precise le mouvement(déplacement).
        :param additive: Si True, la fonction additione la valeur du paramère au position actuelle. Sinon elle va
            remplacer la position actuelle par la valeur donnée.
        :return:
        """
        if additive:
            self.pos += movement
        else:
            self.pos = movement

    def rotate(self, rotation: float, additive=True) -> None:
        """
        Fonction qui permet de modifier la rotation de l'objet.

        :param rotation: La rotation en radian.
        :param additive: Si True, la fonction additione la valeur du paramère au rotation actuelle. Sinon elle va
            remplacer la rotation actuelle par la valeur donnée.
        :return:
        """
        if additive:
            self.rotation += rotation
        else:
            self.rotation = rotation
        self.rotation %= math.pi * 2

    def mscale(self, multiplier: Union[float, int]) -> None:
        """
        Fonction qui permet de modifier l'échelle de l'objet.

        :param multiplier: Multiplicateur de l'échelle.
        :return:
        """
        self.scale *= multiplier

    def scale_to(self, target_scale: Vector2) -> None:
        """
        Fonction qui permet de modifier l'échelle de l'objet.

        :param target_scale: Nouvelle échelle.
        :return:
        """
        self.scale = target_scale


class GameObject(BaseObject, Sprite):
    """
    La base de tous les objets utilisables dans le jeu.
    """
    def __init__(self, pos: Vector2, rotation: float, object_scale: Vector2, image: pygame.Surface, enabled=True,
                 name=""):
        """

        :param pos: La position initiale de l'objet. La valeur par défaut est pygame.Vector2(0, 0).
        :param rotation: La rotation en radian initiale de l'objet. La valeur par défaut est 0.
        :param object_scale: L'échelle initiale de l'objet. La valeur par défaut est pygame.Vector2(1, 1).
        :param image: L'image de l'objet initiale.
        :param enabled: Si l'objet est active quand ce dernier est crée ou pas.
        :param name: Le nom de l'objet.
        """
        super().__init__(pos, rotation, object_scale)
        self.image = image
        self.copy_img = self.image.copy()
        self.rect = self.image.get_rect()
        self.children = None
        self.components = None
        self.enabled = enabled
        self.name = name

    def blit(self, screen: pygame.Surface) -> None:
        """
        Affiche l'objet sur la fenêtre.
        :param screen: La fenêtre où on affiche l'objet.
        :return:
        """
        screen.blit(self.image, self.rect)

    def translate(self, movement: Vector2, additive=True) -> None:
        """
        Fonction qui permet de modifier la position de l'objet.

        :param movement: Un vecteur qui precise le mouvement(déplacement).
        :param additive: Si True, la fonction additione la valeur du paramère au position actuelle. Sinon elle va
            remplacer la position actuelle par la valeur donnée.
        :return:
        """
        super().translate(movement, additive)
        self.rect = self.image.get_rect(center=(self.pos.x, self.pos.y))

    def rotate(self, rotation: float, additive=True) -> None:
        """
        Fonction qui permet de modifier la rotation de l'objet.

        :param rotation: La rotation en radian.
        :param additive: Si True, la fonction additione la valeur du paramère au rotation actuelle. Sinon elle va
           remplacer la rotation actuelle par la valeur donnée.
        :return:
       """
        b4_rct = self.image.get_rect(center=self.rect.center)
        super().rotate(rotation, additive)
        rotated = pygame.transform.rotate(self.copy_img, rad2deg(self.rotation))
        rct = rotated.get_rect(center=b4_rct.center)
        self.image = rotated
        self.rect = rct

    def mscale(self, multiplier: Union[float, int]) -> None:
        pass

    def scale_to(self, target_scale: Vector2) -> None:
        super().scale_to(target_scale)
        pygame.transform.scale(self.image, (target_scale.x, target_scale.y), self.image)

    def start(self):
        pass

    def early_update(self):
        pass

    def update(self):
        pass

    def children_update(self):
        pass

