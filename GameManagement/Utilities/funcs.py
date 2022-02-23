from GameManagement.locals import *


def rad2deg(radian: float) -> float:
    """
    Convertit l'angle en radian en degré

    :param radian: L'angle qu'on veut convertir en degré
    :return: 180 * (radian / pi )
    """
    return RAD2DEG * radian
