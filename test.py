from GameManager.MainLoopManager import GameRoot
from GameManager.resources import load_font, load_img
from GameManager.util import GameObject
from GameManager.locals import *
import GameManager.singleton as sing
import pygame
from pygame.math import Vector2
import math
import os


class TestObject(GameObject):
    def __init__(self, pos: Vector2, rotation: float, image: pygame.Surface, name: str):
        super().__init__(pos, rotation, image, name)

    def update(self) -> None:
        self.rotate(math.pi / 300)
        super().update()


class Test2(GameObject):
    def __init__(self):
        super().__init__(Vector2(0, 0), 0, pygame.Surface((0, 0)), "test2")

    def update(self) -> None:
        sing.ROOT.camera_pos += Vector2(0.1, 0.1)


if __name__ == "__main__":
    root = GameRoot((300, 300), (30, 30, 30), "test game", os.path.dirname(os.path.realpath(__file__)),
                    Vector2(0, 0), 150)
    root.add_gameObject(TestObject(Vector2(0, 0), 0, load_img("resources/test/grid/grid_one.png"), "test_square"))
    root.game_objects["test_square"].children.add_gameobject(
        TestObject(Vector2(0, 30), 0, load_img("resources/test/grid/grid_two.png"), "child"))

    root.add_gameObject(Test2())

    root.mainloop()
