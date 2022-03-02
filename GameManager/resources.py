import pygame
import os
import pathlib
import typing
import GameManager.singleton as sing


def load_img(filename: typing.Union[str, pathlib.Path],
             resize: typing.Optional[tuple[int, int]] = None) -> pygame.Surface:
    loaded = pygame.image.load(os.path.join(sing.ROOT.resources_path, filename)).convert_alpha()
    if resize is None:
        return loaded
    else:
        return pygame.transform.scale(loaded, resize)


def load_font(filename: typing.Union[str, pathlib.Path], font_size: int) -> pygame.font.Font:
    return pygame.font.Font(os.path.join(sing.ROOT.resources_path, filename), font_size)