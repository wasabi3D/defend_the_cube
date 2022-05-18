import pygame
import os
import pathlib
import typing
import GameManager.singleton as sing
from typing import Optional
from GameManager.locals import VOLUME


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
    Fonction pour charger une police

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


def load_sound(filename: typing.Union[str, pathlib.Path], name: str, override_volume: Optional[float] = None) -> None:
    """
    Fonction pour charger un fichier audio

    :param filename: Le nom du fichier
    :param name: Le nom du son chargé
    :param override_volume: Si on souhaite utiliser un volume spécifique ou pas
    """
    sound = pygame.mixer.Sound(os.path.join(sing.ROOT.resources_path, filename))
    if VOLUME in sing.ROOT.parameters and override_volume is None:
        sound.set_volume(sing.ROOT.parameters[VOLUME])
    elif override_volume is not None:
        sound.set_volume(override_volume)
    else:
        sound.set_volume(1)

    sing.ROOT.sounds[name] = sound
