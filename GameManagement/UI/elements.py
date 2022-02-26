from GameManagement.UI.base import BaseUIObject
import GameManagement.locals as loc
import pygame
import typing


class TextLabel(BaseUIObject):
    def __init__(self, pos: pygame.Vector2, rotation: float, object_scale: pygame.Vector2, font: pygame.font.Font,
                 text: str, color: tuple[int, int, int], components: list, antialias=True, anchor=loc.NW):
        super().__init__(pos, rotation, object_scale, font.render(text, antialias, color), components, anchor=anchor)
        self.font: pygame.font.Font = font
        self.text: str = text
        self.color: tuple[int, int, int] = color
        self.antialias: bool = antialias

    def set_text(self, text: str, color: typing.Optional[tuple[int, int, int]] = None,
                 antialias: typing.Optional[bool] = None):
        self.text = text
        if color is not None and isinstance(color, tuple):
            self.color = color
        if antialias is not None and isinstance(antialias, bool):
            self.antialias = antialias
        self.image = self.font.render(self.text, self.antialias, self.color)





