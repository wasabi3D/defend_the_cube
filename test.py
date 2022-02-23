import GameManagement.MainLoopManager as mmg
import GameManagement.SceneManager as smg
import GameManagement.Utilities.Objects as utils

import pygame
from pygame.math import Vector2
import math


class TestObject(utils.GameObject):
    def __init__(self, img, name=""):
        super().__init__(image=img, pos=Vector2(150, 150), rotation=0, object_scale=Vector2(1, 1), name=name)

    def update(self):
        self.rotate(math.pi / 360)
        self.translate(Vector2(0.2, 0.2))
        if self.pos.x > 300:
            self.translate(Vector2(0, self.pos.y), additive=False)
        if self.pos.y > 300:
            self.translate(Vector2(self.pos.x, 0), additive=False)

        super().update()


class TestObject2(utils.GameObject):
    def __init__(self, img, name=""):
        super().__init__(image=img, pos=Vector2(20, -20), rotation=0, object_scale=Vector2(1, 1), name=name)
        self.mov = Vector2(1, 0)

    def update(self):
        self.rotate(math.pi / 480)
        if self.pos.x > 50 or self.pos.x < -50:
            self.mov.x *= -1

        self.translate(self.mov, True)
        super().update()


class TestObject3(utils.GameObject):
    def __init__(self, img, name=""):
        super().__init__(image=img, pos=Vector2(0, -30), rotation=0, object_scale=Vector2(1, 1), name=name)
        self.mov = Vector2(0, 0.05)

    def update(self):
        self.rotate(math.pi / 480)
        if self.pos.y > 50 or self.pos.y < -50:
            self.mov.y *= -1

        self.translate(self.mov, True)


class TestScene(smg.Scene):
    def __init__(self):
        super().__init__()
        test = TestObject(pygame.image.load(r"resources/test/grid/grid_one.png"))
        test2 = TestObject2(pygame.image.load(r"resources/test/grid/grid_two.png"), name="child")
        test3 = TestObject3(pygame.image.load(r"resources/test/grid/grid_three.png"), name="child of child")
        test2.children.add_gameobject(test3, test2)
        test.children.add_gameobject(test2, test)
        self.gameObjects.append(test)


root = mmg.GameRoot((300, 300), (30, 30, 30), fps_limit=150)
root.register(TestScene())
root.mainloop()
