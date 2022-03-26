from GameManager.util import GameObject

import pygame
from pygame.math import Vector2


class TestEnemy(GameObject):
    def __init__(self, pos: Vector2, image: pygame.Surface, name: str):
        super().__init__(pos, 0, image, name)
