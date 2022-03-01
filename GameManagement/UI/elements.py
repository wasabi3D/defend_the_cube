from GameManagement.UI.base import BaseUIObject
import GameManagement.locals as loc
import GameManagement.SceneManager as Sm
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


class Button(BaseUIObject):
    def __init__(self, pos: pygame.Vector2, rotation: float, object_scale: pygame.Vector2, image: pygame.Surface,
                 on_click_funcs: list, components: list, anchor=loc.NW):
        super().__init__(pos, rotation, object_scale, image, components, anchor=anchor)
        self.on_click = on_click_funcs
        self.on_click_anim_tick = 0

    def early_update(self, scene: Sm.Scene) -> None:
        if self.on_click_anim_tick > 0:
            a = int(self.surf_mult[0] + 70 / 20)
            self.surf_mult = (a, a, a, self.surf_mult[3])
            print(self.surf_mult)
            self.on_click_anim_tick -= 1
            if self.on_click_anim_tick == 0:
                self.surf_mult = (190, 190, 190, self.surf_mult[3])

    def on_mouse_click_down(self, scene: Sm.Scene, mouse_pos: pygame.Vector2, button: int):
        for f in self.on_click:
            f(scene, mouse_pos, button)
        self.surf_mult = (120, 120, 120, self.surf_mult[3])
        self.on_click_anim_tick = 20

    def on_mouse_rect_enter(self, scene: Sm.Scene, mouse_pos: pygame.Vector2):
        self.surf_mult = (190, 190, 190, self.surf_mult[3])

    def on_mouse_rect_exit(self, scene: Sm.Scene, mouse_pos: pygame.Vector2):
        self.surf_mult = (255, 255, 255, self.surf_mult[3])

    def get_screen_pos(self) -> pygame.Vector2:
        a = super().get_screen_pos()
        return a



