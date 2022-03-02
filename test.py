from GameManager.MainLoopManager import GameRoot
from GameManager.resources import load_font, load_img
from GameManager.util import GameObject
from GameManager.locals import *
import GameManager.singleton as sing
import pygame
from pygame.math import Vector2
from pygame.locals import *
from generate_terrain import Terrain
import math
import os


class TestObject(GameObject):
    def __init__(self, pos: Vector2, rotation: float, image: pygame.Surface, name: str):
        super().__init__(pos, rotation, image, name)

    def update(self) -> None:
        self.rotate(math.pi / 300)
        super().update()


class CameraMove(GameObject):
    def __init__(self):
        super().__init__(Vector2(0, 0), 0, pygame.Surface((0, 0)), "test2")

    def update(self) -> None:
        pressed = pygame.key.get_pressed()
        if pressed[K_UP]:
            sing.ROOT.camera_pos += Vector2(0, -2)
        if pressed[K_DOWN]:
            sing.ROOT.camera_pos += Vector2(0, 2)
        if pressed[K_RIGHT]:
            sing.ROOT.camera_pos += Vector2(2, 0)
        if pressed[K_LEFT]:
            sing.ROOT.camera_pos += Vector2(-2, 0)
        print(sing.ROOT.delta)


if __name__ == "__main__":
    root = GameRoot((300, 300), (30, 30, 30), "test game", os.path.dirname(os.path.realpath(__file__)),
                    Vector2(0, 0), 150)

    bs = 10
    biomes = [load_img("resources/test/grid/dark_grass.png", (bs, bs)),
              load_img("resources/test/grid/grid_two.png", (bs, bs))]
    ter = Terrain(500, (50, 50), biomes, bs)

    root.add_gameObject(ter)
    root.add_gameObject(CameraMove())

    root.mainloop()
