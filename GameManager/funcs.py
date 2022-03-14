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
    return pygame.Vector2(t[0], t[1])


def is_included(pos: pygame.Vector2, rect: pygame.Rect):
    return (rect.x <= pos.x <= rect.x + rect.width) and (rect.y <= pos.y <= rect.y + rect.height)


def resize_surface(surf: pygame.Surface, multiplier: float) -> pygame.Surface:
    s = tuple2Vec2(surf.get_size()) * multiplier
    print(s)
    return pygame.transform.smoothscale(surf, (s.x, s.y))

