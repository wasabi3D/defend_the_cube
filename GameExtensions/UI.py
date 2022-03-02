from GameManager.util import GameObject
from GameExtensions.locals import N, NE, NW, S, SE, SW, E, W, CENTER
import GameManager.singleton as sing
from pygame.math import Vector2
import pygame
import typing


class BaseUIObject(GameObject):
    def __init__(self, pos: Vector2,
                 rotation: float,
                 image: pygame.Surface,
                 name: str,
                 anchor: str = NW):
        super().__init__(pos, rotation, image, name)
        self.anchor = anchor

    def get_real_pos(self) -> pygame.Vector2:
        pre = super().get_real_pos()
        if self.parent is None:
            x_modif = sing.ROOT.screen_dim[0] / 2
            y_modif = sing.ROOT.screen_dim[1] / 2
            # sing.ROOT.cur_scene.main_camera.pos +
            pre += pygame.Vector2(x_modif, y_modif)
        else:
            x_modif = self.parent.rect.width / 2
            y_modif = self.parent.rect.height / 2

        if self.anchor == CENTER:
            return pre
        elif self.anchor == N:
            return pre + pygame.Vector2(0, -y_modif)
        elif self.anchor == E:
            return pre + pygame.Vector2(x_modif, 0)
        elif self.anchor == S:
            return pre + pygame.Vector2(0, y_modif)
        elif self.anchor == W:
            return pre + pygame.Vector2(-x_modif, 0)
        elif self.anchor == NE:
            return pre + pygame.Vector2(x_modif, -y_modif)
        elif self.anchor == SE:
            return pre + pygame.Vector2(x_modif, y_modif)
        elif self.anchor == SW:
            return pre + pygame.Vector2(-x_modif, y_modif)
        elif self.anchor == NW:
            return pre + pygame.Vector2(-x_modif, -y_modif)

    def get_screen_pos(self) -> pygame.Vector2:
        # return self.get_real_pos() - pygame.Vector2(sing.ROOT.screen_dim[0] / 2, sing.ROOT.screen_dim[1] / 2)
        return self.get_real_pos()

    def blit(self, screen: pygame.Surface) -> None:
        pos = self.get_real_pos()
        screen.blit(self.alpha_converted(), self.image.get_rect(center=(pos.x, pos.y)))
        for child in self.children.values():
            child.blit(screen)


class TextLabel(BaseUIObject):
    def __init__(self, pos: pygame.Vector2, rotation: float, font: pygame.font.Font,
                 text: str, color: tuple[int, int, int], name: str, antialias=True, anchor=NW):
        super().__init__(pos, rotation, font.render(text, antialias, color), name, anchor=anchor)
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
