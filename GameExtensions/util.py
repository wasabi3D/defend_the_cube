import typing
from typing import Union
import math
import pygame
from GameManager.resources import load_img


class ShakeGenerator:
    """
    Classe qui permet de générer un tremblement.
    """
    def __init__(self,
                 x_intensity: Union[int, float],
                 y_intensity: Union[int, float],
                 x_cycle: Union[int, float],
                 y_cycle: Union[int, float],
                 x_offset: Union[int, float],
                 y_offset: Union[int, float],
                 x_intensity_decay: Union[int, float],
                 y_intensity_decay: Union[int, float],
                 wave_func=math.sin):
        """
        :param x_intensity: Intensité du tremblement de l'abscisse
        :param y_intensity: Intensité du tremblement de l'ordonnée
        :param x_cycle: Modifie la période du tremblement de l'abscisse
        :param y_cycle: Modifie la période du tremblement de l'ordonnée
        :param x_offset: Décale la période de l'abscisse d'un certain temps
        :param y_offset: Décale la période de l'ordonnée d'un certain temps
        :param x_intensity_decay: Comment diminuer l'intensité du tremblement de l'abcisse à chaque frame
        :param y_intensity_decay: Comment diminuer l'intensité du tremblement de l'ordonnée à chaque frame
        :param wave_func: Fonction periodique utilisée pour générer le tremblement
        """
        self.x_intensity = x_intensity
        self.y_intensity = y_intensity
        self.x_cycle = x_cycle
        self.y_cycle = y_cycle
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.x_intensity_decay = x_intensity_decay
        self.y_intensity_decay = y_intensity_decay
        self.f = wave_func

        self.time = 0
        self.cur_x_int = 0
        self.cur_y_int = 0
        self.shaking = False
        self.shake_stop_threshold = 0.001

    def begin(self, time=0) -> None:
        """
        Commence et initialise la génération du tremblement
        :param time: Le point de départ
        """
        self.time = time
        self.cur_x_int = self.x_intensity
        self.cur_y_int = self.y_intensity
        self.shaking = True

    def next_frame(self, delta: Union[float, int]) -> None:
        """
        Fait avancer le tremblement d'un certain temps
        :param delta: Variation de temps entre 2 frame consécutifs
        """
        if self.shaking:
            self.cur_x_int *= self.x_intensity_decay
            self.cur_y_int *= self.y_intensity_decay
            self.time += delta

            if self.cur_x_int < self.shake_stop_threshold and self.cur_y_int < self.shake_stop_threshold:
                self.shaking = False

    def get_shake(self) -> pygame.Vector2:
        """
        Génére le tremblement à t=self.time
        :return: Un pygame.Vector2 qui représente le tremblement
        """
        if self.shaking:
            return pygame.Vector2(self.cur_x_int * self.f(self.time * self.x_cycle + self.x_offset),
                                  self.cur_y_int * self.f(self.time * self.y_cycle + self.y_offset))
        else:
            return pygame.Vector2(0, 0)


class Animation:
    def __init__(self, frames: list[pygame.Surface], frame_interval: float):
        self.frames = frames
        self.interval = frame_interval


class Animator:
    def __init__(self):
        self.animations: dict[str, Animation] = {}
        self.current: typing.Optional[str] = None
        self.cur_frame = 0
        self.timer = 0

    def register_anim(self, name: str, anim: Animation) -> None:
        self.animations.setdefault(name, anim)

    def start_anim(self, name: str):
        self.current = name
        self.cur_frame = 0
        self.timer = 0

    def update(self, delta: float):
        if self.current is None:
            return
        self.timer += delta
        if self.animations[self.current].interval <= self.timer:
            self.cur_frame += 1
            self.cur_frame %= len(self.animations[self.current].frames)
            self.timer = 0

    def get_cur_frame(self) -> pygame.Surface:
        return self.animations[self.current].frames[self.cur_frame]

    @staticmethod
    def load_frames_by_pattern(base_file_name: str, suffix: str, start_i: int, end_i: int, conv=lambda s: s,
                               override_size: typing.Optional[tuple[int, int]] = None):
        lst = []
        for i in range(start_i, end_i + 1):
            lst.append(conv(load_img(f"{base_file_name}{i}{suffix}", override_size)))
        return lst

