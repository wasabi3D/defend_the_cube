from GameManagement.locals import *
import pygame


def rad2deg(radian: float) -> float:
    """
    Convertit l'angle en radian en degré

    :param radian: L'angle qu'on veut convertir en degré
    :return: 180 * (radian / pi )
    """
    return RAD2DEG * radian


def do_intersect(rect1: pygame.Rect, rect2: pygame.Rect) -> bool:
    """
    Fonction qui permet de savoir si 2 rects sont en intersection.
    :param rect1: Une rect
    :param rect2: Une autre rect
    :return: True si c'est le cas, False sinon.
    """
    return (rect1.x <= rect2.x <= rect1.width + rect1.x or rect2.x <= rect1.x <= rect2.x + rect2.width) and \
           (rect1.y <= rect2.y <= rect1.height + rect1.y or rect2.y <= rect1.y <= rect2.y + rect2.height)
