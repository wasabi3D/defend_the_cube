from GameManager.locals import *
import pygame
import typing


def rad2deg(radian: float) -> float:
    """
    Convertit l'angle en radian en degré

    :param radian: L'angle qu'on veut convertir en degré
    :return: 180 * (radian / pi )
    """
    return RAD2DEG * radian


def tuple2Vec2(t: typing.Union[tuple[int, int], tuple[float, float]]) -> pygame.Vector2:
    """
    Fonction pour convertir un tuple en pygame.Vector2

    :param t: Le tuple qu'on convertit
    :return: Le vector2 converti
    """
    return pygame.Vector2(t[0], t[1])


def is_included(pos: pygame.Vector2, rect: pygame.Rect):
    """
    Vérifie si les coordonnées donnés sont inclus dans la rect donnée

    :param pos: Les coordonnées
    :param rect: La rect qui represente la zone
    :return: True si inclus, False sinon
    """
    return (rect.x <= pos.x <= rect.x + rect.width) and (rect.y <= pos.y <= rect.y + rect.height)


def resize_surface(surf: pygame.Surface, multiplier: float) -> pygame.Surface:
    """
    Modifie la taille d'une image donnée

    :param surf: L'image
    :param multiplier: Grossissement
    :return: L'image modifiée
    """
    s = tuple2Vec2(surf.get_size()) * multiplier
    return pygame.transform.scale(surf, (s.x, s.y))

