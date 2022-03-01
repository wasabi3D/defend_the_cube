import GameManagement.MainLoopManager as mmg
import GameManagement.SceneManager as smg
import GameManagement.Utilities.Objects as utils
import GameManagement.Utilities.Components as cmps
import GameManagement.Extra.rendering as ex
import GameManagement.singleton as sing
from GameManagement.Utilities.funcs import tuple2Vec2
from GameManagement.locals import *
from pygame.locals import *
from GameManagement.UI.elements import TextLabel
from GameManagement.Resources import load_font, load_img

import pygame
from pygame.math import Vector2
import math
import os


class TestObject(utils.GameObject):
    def __init__(self, img, name=""):
        super().__init__(image=img, pos=Vector2(0, 0), rotation=0, object_scale=Vector2(1, 1), name=name,
                         components=[])

    def normal_update(self, scene: smg.Scene):
        # self.rotate(math.pi / 360)
        # self.translate(Vector2(0.2, 0.2))
        # if self.pos.x > 300:
        #     self.translate(Vector2(0, self.pos.y), additive=False)
        # if self.pos.y > 300:
        #     self.translate(Vector2(self.pos.x, 0), additive=False)

        if K_LEFT in sing.ROOT.key_downs:
            self.translate(Vector2(-10, 0))
        if K_RIGHT in sing.ROOT.key_downs:
            self.translate(Vector2(10, 0))

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
        self.a_mov = 1

    def normal_update(self, scene: smg.Scene):
        self.rotate(math.pi / 480)
        if self.pos.y > 50 or self.pos.y < -50:
            self.mov.y *= -1

        if self.surf_mult[3] == 255 or self.surf_mult[3] == 0:
            self.a_mov *= -1

        self.set_alpha(self.a_mov, additive=True)
        self.translate(self.mov, True)


class TestScene(smg.Scene):
    def __init__(self):
        super().__init__()
        test = TestObject(load_img(r"resources/test/grid/grid_one.png"))
        test2 = TestObject2(load_img(r"resources/test/grid/grid_two.png"), name="child")
        test3 = TestObject3(load_img(r"resources/test/grid/grid_three.png"), name="child of child")
        test2.children.add_gameobject(test3)
        test.children.add_gameobject(test2)
        self.add_gameobject(test)

        lb = TextLabel(Vector2(50, 10), 0, Vector2(1, 1), load_font("resources/test/fonts/remachine.ttf", 24),
                       "Test text", (200, 200, 200), [], anchor=NW)
        self.add_gameobject(lb, name="test label")

        camera = ex.Camera(Vector2(0, 0), 0)
        self.register_main_camera(camera)


root = mmg.GameRoot((300, 300), (30, 30, 30), "test game", fps_limit=150,
                    resources_root_path=os.path.dirname(os.path.realpath(__file__)))
root.register(TestScene())
root.mainloop()
