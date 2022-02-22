import GameManagement.MainLoopManager as mmg
import GameManagement.SceneManager as smg
import GameManagement.Utilities as utils
import pygame
from pygame.math import Vector2
import math


class TestObject(utils.GameObject):
    def __init__(self, img):
        super().__init__(image=img, pos=Vector2(50, 50), rotation=0, object_scale=Vector2(1, 1))

    def update(self):
        self.rotate(math.pi / 48)
        self.translate(Vector2(1, 1))
        if self.pos.x > 300:
            self.translate(Vector2(0, self.pos.y), additive=False)
        if self.pos.y > 300:
            self.translate(Vector2(self.pos.x, 0), additive=False)


class TestScene(smg.Scene):
    def __init__(self):
        super().__init__()
        test = TestObject(pygame.image.load(r"resources/test/grid/grid_one.png"))
        self.gameObjects.append(test)


root = mmg.GameRoot((300, 300), (30, 30, 30))
root.register(TestScene())
root.mainloop()
