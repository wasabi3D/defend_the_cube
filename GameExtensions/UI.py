from GameExtensions.locals import N, NE, NW, S, SE, SW, E, W, CENTER

from GameManager.util import GameObject
import GameManager.singleton as sing
from GameManager.resources import load_img
from GameManager.locals import MOUSE_LEFT

import pygame
from pygame.math import Vector2

import typing


class BaseUIObject(GameObject):
    """La classe que tous les autres objets UI vont succéder(inherit)
    """
    def __init__(self, pos: Vector2,
                 rotation: float,
                 image: pygame.Surface,
                 name: str,
                 anchor: str = NW):
        """

        :param pos: La position sur l'écran
        :param rotation: La rotation initiale
        :param image: L'image affichée
        :param name: Le nom de cette UI
        :param anchor: Définit où est le (0, 0): Par exemple si anchor=N, le (0, 0) sera en haut au millieu de
            l'écran, si anchor=SW, le (0, 0) sera en bas à gauche de l'écran.
        """
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
        else:
            return pre

    def get_screen_pos(self) -> pygame.Vector2:
        # return self.get_real_pos() - pygame.Vector2(sing.ROOT.screen_dim[0] / 2, sing.ROOT.screen_dim[1] / 2)
        return self.get_real_pos()

    def blit(self, screen: pygame.Surface, apply_alpha=True) -> None:
        pos = self.get_real_pos()
        screen.blit(self.alpha_converted() if apply_alpha else self.image, self.image.get_rect(center=(pos.x, pos.y)))
        for child in self.children.values():
            child.blit(screen, apply_alpha)


class TextLabel(BaseUIObject):
    """Permet d'afficher un texte (et modifier!) facilement"""
    def __init__(self, pos: pygame.Vector2, rotation: float, font: pygame.font.Font,
                 text: str, color: tuple[int, int, int], name: str, antialias=True, anchor=NW):
        """

        :param pos: La position sur l'écran
        :param rotation: La rotation initiale
        :param font: La police
        :param text: Le texte qu'on souhaite afficher
        :param color: La couleur du texte
        :param name: Le nom
        :param antialias: Si on applique l'antialias ou pas
        :param anchor: Un str qui permet de définir où est le (0, 0)
        """
        super().__init__(pos, rotation, font.render(text, antialias, color), name, anchor=anchor)
        self.font: pygame.font.Font = font
        self.text: str = text
        self.color: tuple[int, int, int] = color
        self.antialias: bool = antialias

    def set_text(self, text: str, color: typing.Optional[tuple[int, int, int]] = None,
                 antialias: typing.Optional[bool] = None):
        """
        Fonction pour afficher un nouveau texte.

        :param text: Le nouveau texte
        :param color: La nouvelle couleur
        :param antialias: Si on applique l'antialias ou pas
        """
        self.text = text
        if color is not None and isinstance(color, tuple):
            self.color = color
        if antialias is not None and isinstance(antialias, bool):
            self.antialias = antialias
        self.image = self.font.render(self.text, self.antialias, self.color)
        self.rect = self.image.get_rect(center=self.pos)


class FPS_Label(TextLabel):
    """
    Une classe pour juste afficher l'FPS du jeu.
    """
    def __init__(self, pos: pygame.Vector2):
        """

        :param pos: Position initiale
        """
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
    """
    La classe pour la barre qui affiche l'HP
    """
    SIZE = (480, 48)

    class RedFill(BaseUIObject):
        """
        La partie rouge de la barre
        """
        def __init__(self, prop: float, size):
            """

            :param prop: Proportion de la taille par rapport à l'image originale
            """
            super().__init__(Vector2(0, 0), 0, load_img("resources/UI/hp_bar_fill.png", size), "red",
                             anchor=CENTER)
            self.prop = prop

        def blit(self, screen: pygame.Surface, apply_alpha=False) -> None:
            rect = self.image.get_rect(center=self.get_real_pos())
            rect.update(rect.left, rect.top, rect.width * self.prop, rect.height)
            screen.blit(self.image, rect.topleft, (0, 0, rect.width, rect.height))

    def __init__(self, pos: Vector2, anchor: str, proportion=1, size=(480, 48)):
        """

        :param pos: La position sur l'écran
        :param anchor: Un str qui permet de définir où est le (0, 0)
        :param proportion: Proportion de la taille de la barre rouge par rapport à l'image originale
        """
        super().__init__(pos, 0, load_img("resources/UI/hp_bar_frame.png", size), "HPBar", anchor=anchor)

        self.prop = proportion
        self.children.add_gameobject(HPBar.RedFill(self.prop, size))
        self.size = size

    def blit(self, screen: pygame.Surface, apply_alpha=False) -> None:
        self.children["red"].prop = self.prop
        super().blit(screen, apply_alpha)


class Button(BaseUIObject):
    HOVERING_ALPHA = 210
    CLICKED_ALPHA = 155
    CL_ALPH_DURATION = 0.02

    def __init__(self,
                 pos: Vector2,
                 rotation: float,
                 image: pygame.Surface,
                 name: str,
                 on_mouse_down_func=None,
                 on_mouse_up_func=None,
                 text: typing.Optional[str] = None,
                 font: typing.Optional[pygame.font.Font] = None,
                 text_color: typing.Optional[tuple[int, int, int]] = None,
                 anchor=NW):
        super().__init__(pos, rotation, image, name, anchor=anchor)
        self.mouse_down_f = on_mouse_down_func
        self.mouse_up_f = on_mouse_up_func
        self.timer = 0
        self.clicking = False
        self.hovering = False
        if text is None:
            self.text = False
        else:
            self.text = True
            txt_font = font if font is not None else pygame.font.SysFont("Arial", 16, False, False)
            label = TextLabel(Vector2(0, 0), 0, txt_font, text, text_color, "text_label", True, CENTER)
            self.children.add_gameobject(label)

    def early_update(self) -> None:
        super().early_update()
        if self.surf_mult.r != 255 and not self.clicking:
            self.timer += sing.ROOT.delta
            if self.timer >= Button.CL_ALPH_DURATION:
                value = 255 if not self.hovering else Button.HOVERING_ALPHA
                self.surf_mult.set_rgb(value)
                self.change_text_rgb(value)

    def on_mouse_down(self, button: int):
        if button == MOUSE_LEFT:
            self.timer = 0
            self.clicking = True
            self.surf_mult.set_rgb(Button.CLICKED_ALPHA)
            self.change_text_rgb(Button.CLICKED_ALPHA)
            if self.mouse_down_f is not None:
                self.mouse_down_f()

    def on_mouse_up(self, button: int):
        if button == MOUSE_LEFT:
            self.clicking = False
            if self.mouse_up_f is not None:
                self.mouse_up_f()

    def on_mouse_rect_enter(self):
        self.surf_mult.set_rgb(Button.HOVERING_ALPHA)
        self.change_text_rgb(Button.HOVERING_ALPHA)
        self.hovering = True

    def on_mouse_rect_exit(self):
        self.surf_mult.set_rgb(255)
        self.change_text_rgb(255)
        self.hovering = False

    def change_text_rgb(self, value: int) -> None:
        if self.text:
            self.children["text_label"].surf_mult.set_rgb(value)


class MenuManager(GameObject):
    def __init__(self, name="MenuManager"):
        super().__init__(Vector2(0, 0), 0, pygame.Surface((0, 0)), name)
        self.menus: dict[str, GameObject] = {"": GameObject(Vector2(0, 0), 0, pygame.Surface((0, 0)), "")}
        self.current: str = ""

    def add_menus(self, *menus: GameObject):
        for menu in menus:
            self.menus[menu.name] = menu

    def switch_menu(self, next_menu_name: str):
        self.current = next_menu_name

    def early_update(self) -> None:
        self.menus[self.current].early_update()

    def update(self) -> None:
        self.menus[self.current].early_update()

    def blit(self, screen: pygame.Surface, apply_alpha=True) -> None:
        self.menus[self.current].blit(screen, apply_alpha)





