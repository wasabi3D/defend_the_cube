import GameManagement.MainLoopManager as mmg
import GameManagement.SceneManager as smg
import GameManagement.Utilities.Objects as utils
import GameManagement.Extra as ex

import pygame
from pygame.math import Vector2
import math


class TestObject(utils.GameObject):
    def __init__(self, img, name=""):
        super().__init__(image=img, pos=Vector2(150, 150), rotation=0, object_scale=Vector2(1, 1), name=name,
                         components=[])

    def normal_update(self, scene: smg.Scene):
        # self.rotate(math.pi / 360)
        # self.translate(Vector2(0.2, 0.2))
        if self.pos.x > 300:
            self.translate(Vector2(0, self.pos.y), additive=False)
        if self.pos.y > 300:
            self.translate(Vector2(self.pos.x, 0), additive=False)

        super().normal_update(scene)


class TestObject2(utils.GameObject):
    def __init__(self, img, name=""):
        super().__init__(image=img, pos=Vector2(20, -20), rotation=0, object_scale=Vector2(1, 1), name=name,
                         components=[])
        self.mov = Vector2(1, 0)

    def normal_update(self, scene: smg.Scene):
        self.rotate(math.pi / 480)
        if self.pos.x > 50 or self.pos.x < -50:
            self.mov.x *= -1

        self.translate(self.mov, True)
        super().normal_update(scene)


class TestObject3(utils.GameObject):
    def __init__(self, img, name=""):
        super().__init__(image=img, pos=Vector2(0, -30), rotation=0, object_scale=Vector2(1, 1), name=name,
                         components=[])
        self.mov = Vector2(0, 0.05)

    def normal_update(self, scene: smg.Scene):
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
        test2.children.add_gameobject(test3)
        test.children.add_gameobject(test2)
        self.add_gameobject(test)

        self.register_main_camera(ex.Camera(Vector2(0, 0), 0))


root = mmg.GameRoot((300, 300), (30, 30, 30), "test game", fps_limit=150)
root.register(TestScene())
root.mainloop()
