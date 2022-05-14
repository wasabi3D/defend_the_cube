import pygame
import os
import pathlib
import typing
import GameManager.singleton as sing


def load_img(filename: typing.Union[str, pathlib.Path],
             resize: typing.Optional[tuple[int, int]] = None) -> pygame.Surface:
    """
    Fonction pour charger une image

    :param filename: Le nom du fichier
    :param resize: Un tuple pour la nouvelle taille éventuellement
    :return: L'image chargée
    """
    loaded = pygame.image.load(os.path.join(sing.ROOT.resources_path, filename)).convert_alpha()
    if resize is None:
        return loaded
    else:
        return pygame.transform.scale(loaded, resize)


def load_font(filename: typing.Union[str, pathlib.Path], font_size: int, global_font=False, name="")\
        -> pygame.font.Font:
    """
    Fcontion pour charger une police

    :param filename: Le nom du fichier
    :param font_size: La taille de la police
    :param global_font: Si on souhaite utiliser cette police partout ou pas
    :param name: Le nom de la police si global_font == True
    :return: La police chargée
    """
    fnt = pygame.font.Font(os.path.join(sing.ROOT.resources_path, filename), font_size)
    if global_font:
        sing.ROOT.global_fonts.setdefault(name, fnt)
    return fnt
