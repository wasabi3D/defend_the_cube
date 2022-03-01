from GameManagement.UI.base import BaseUIObject
import GameManagement.locals as loc
import GameManagement.SceneManager as Sm
from GameManagement.Utilities.funcs import tuple2Vec2
import pygame
import typing


class TextLabel(BaseUIObject):
    def __init__(self, pos: pygame.Vector2, rotation: float, object_scale: pygame.Vector2, font: pygame.font.Font,
                 text: str, color: tuple[int, int, int], name: str, components: list, antialias=True, anchor=loc.NW):
        super().__init__(pos, rotation, object_scale, font.render(text, antialias, color), name,
                         components, anchor=anchor)
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
                 name: str,
                 on_click_funcs: list, components: list, anchor=loc.NW):
        super().__init__(pos, rotation, object_scale, image, name, components, anchor=anchor)
        self.on_click = on_click_funcs
        self.on_click_anim_tick = 0

    def early_update(self, scene: Sm.Scene) -> None:
        if self.on_click_anim_tick > 0:
            self.surf_mult.add_rgb(70 / 20)  # GENERALISER
            self.on_click_anim_tick -= 1
            if self.on_click_anim_tick == 0:
                self.surf_mult.set_rgb(190)

    def on_mouse_click_down(self, scene: Sm.Scene, mouse_pos: pygame.Vector2, button: int):
        for f in self.on_click:
            f(scene, mouse_pos, button)
        if button == loc.MOUSE_LEFT:
            self.surf_mult.set_rgb(120)
            self.on_click_anim_tick = 20

    def on_mouse_rect_enter(self, scene: Sm.Scene, mouse_pos: pygame.Vector2):
        self.surf_mult.set_rgb(190)

    def on_mouse_rect_exit(self, scene: Sm.Scene, mouse_pos: pygame.Vector2):
        self.surf_mult.set_rgb(255)

    def get_screen_pos(self) -> pygame.Vector2:
        a = super().get_screen_pos()
        return a


class Draggable(Button):
    def __init__(self, pos: pygame.Vector2, rotation: float, object_scale: pygame.Vector2, image: pygame.Surface,
                 name: str, on_click_funcs: list, components: list, anchor=loc.NW):
        super().__init__(pos, rotation, object_scale, image, name, on_click_funcs, components, anchor=anchor)
        self.is_dragging = False
        self.last_mouse_pos: pygame.Vector2 = pygame.Vector2(0, 0)

    def early_update(self, scene: Sm.Scene) -> None:
        super().early_update(scene)
        if self.is_dragging:
            cur_pos = tuple2Vec2(pygame.mouse.get_pos())
            self.translate(cur_pos - self.last_mouse_pos, additive=True)
            self.last_mouse_pos = cur_pos

    def on_mouse_click_down(self, scene: Sm.Scene, mouse_pos: pygame.Vector2, button: int):
        super().on_mouse_click_down(scene, mouse_pos, button)
        if button == loc.MOUSE_LEFT:
            self.is_dragging = True
            self.last_mouse_pos = tuple2Vec2(pygame.mouse.get_pos())

    def on_mouse_click_up(self, scene: Sm.Scene, mouse_pos: pygame.Vector2, button: int):
        super().on_mouse_click_up(scene, mouse_pos, button)
        if button == loc.MOUSE_LEFT:
            self.is_dragging = False



