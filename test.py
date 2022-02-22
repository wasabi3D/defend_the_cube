import GameManagement.MainLoopManager as mmg
import GameManagement.SceneManager as smg
import GameManagement.Utilities as utils
import pygame
from pygame.math import Vector2


class TestObject(utils.GameObject):
    def __init__(self, img):
        super().__init__(image=img, pos=Vector2(5, 5), rotation=0, object_scale=Vector2(1, 1))

    def update(self):
        self.translate(pygame.math.Vector2(0.05, 0.05))


class TestScene(smg.Scene):
    def __init__(self):
        super().__init__()
        test = TestObject(pygame.image.load(r"resources/test/grid/grid_one.png"))
        self.gameObjects.append(test)


root = mmg.GameRoot((300, 300), (30, 30, 30))
root.register(TestScene())
root.mainloop()
