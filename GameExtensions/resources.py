from GameManager.util import GameObject
from GameManager.resources import load_img
from pygame.math import Vector2
import pygame
from random import randint


class Tree(GameObject):
    def __init__(self, pos: Vector2, name: str, size_min=96, size_max=128):
        size = randint(size_min, size_max)
        super().__init__(pos, 0, load_img("resources/environment/tree.png", (size, size)), name)
        self.rect_surf = pygame.Surface((size * 0.4, size * 0.4))
        self.col_offset = Vector2(0, 30)

    def get_collision_rect(self) -> pygame.Rect:
        # print(f"TREE {self.rect_surf.get_rect(center=self.get_real_pos() + self.col_offset)}")
        return self.rect_surf.get_rect(center=self.get_real_pos() + self.col_offset)
