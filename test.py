from GameManager.MainLoopManager import GameRoot
from GameManager.resources import load_font, load_img
from GameManager.util import GameObject
from GameManager.locals import *
import GameManager.singleton as sing
from GameExtensions.UI import TextLabel
from GameExtensions.locals import *
import pygame
from pygame.math import Vector2
from pygame.locals import *
from generate_terrain import Terrain
import math
import os


class TestObject(GameObject):
    def __init__(self, pos: Vector2, rotation: float, image: pygame.Surface, name: str):
        super().__init__(pos, rotation, image, name)

    def on_mouse_down(self, button: int):
        print("cc")

    def on_mouse_rect_exit(self):
        print("exit")


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


if __name__ == "__main__":
    root = GameRoot((550, 550), (30, 30, 30), "test game", os.path.dirname(os.path.realpath(__file__)),
                    Vector2(0, 0), 150)

    bs = 30
    biomes = [load_img("resources/test/grid/dark_grass.png", (bs, bs)),
              load_img("resources/test/grid/grass.png", (bs, bs))]
    ter = Terrain(500, (150, 150), biomes, bs)

    root.add_gameObject(ter)
    root.add_gameObject(CameraMove())
    root.add_gameObject(TestObject(Vector2(0, 0), 0, load_img("resources/test/grid/grid_one.png"), "test_obj"))
    root.add_gameObject(TextLabel(Vector2(30, 30), 0, load_font("resources/test/fonts/remachine.ttf", 25),
                                  "hello world", (200, 200, 200), "test_label", anchor=CENTER))

    root.mainloop()
