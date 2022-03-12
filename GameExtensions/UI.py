from GameManager.util import GameObject
from GameExtensions.locals import N, NE, NW, S, SE, SW, E, W, CENTER
import GameManager.singleton as sing
from GameManager.resources import load_img
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

    def blit(self, screen: pygame.Surface, apply_alpha=True) -> None:
        pos = self.get_real_pos()
        screen.blit(self.alpha_converted(), self.image.get_rect(center=(pos.x, pos.y)))
        for child in self.children.values():
            child.blit(screen, apply_alpha)


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
        self.rect = self.image.get_rect(center=self.pos)


class FPS_Label(TextLabel):
    def __init__(self, pos: pygame.Vector2):
        super().__init__(pos, 0, pygame.font.SysFont("Arial", 23, bold=True), "",
                         (255, 50, 100), "fps_display")
        self.tick_cnt = 0
        self.sum = 0

    def update(self) -> None:
        self.tick_cnt += 1
        self.sum += sing.ROOT.delta
        if sing.ROOT.delta != 0 and self.tick_cnt % 60 == 0:
            self.set_text(f"{int(1 / (self.sum / 60))} FPS")
            self.sum = 0

    def blit(self, screen: pygame.Surface, apply_alpha=False) -> None:
        super().blit(screen, apply_alpha=apply_alpha)


class HPBar(BaseUIObject):
    SIZE = (480, 48)

    class RedFill(BaseUIObject):
        def __init__(self, prop: float):
            super().__init__(Vector2(0, 0), 0, load_img("resources/UI/hp_bar_fill.png", HPBar.SIZE), "red",
                             anchor=CENTER)
            self.prop = prop

        def blit(self, screen: pygame.Surface, apply_alpha=False) -> None:
            rect = self.image.get_rect(center=self.get_real_pos())
            rect.update(rect.left, rect.top, rect.width * self.prop, rect.height)
            screen.blit(self.image, rect.topleft, (0, 0, rect.width, rect.height))

    def __init__(self, pos: Vector2, anchor: str, proportion=1):
        super().__init__(pos, 0, load_img("resources/UI/hp_bar_frame.png", HPBar.SIZE), "HPBar", anchor=anchor)

        self.prop = proportion
        self.children.add_gameobject(HPBar.RedFill(self.prop))

    def blit(self, screen: pygame.Surface, apply_alpha=False) -> None:
        self.children["red"].prop = self.prop
        super().blit(screen, apply_alpha)


