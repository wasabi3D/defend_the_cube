import GameManagement.MainLoopManager as mmg
import GameManagement.SceneManager as smg
import GameManagement.Utilities.Objects as utils
import GameManagement.Utilities.Components as cmps
import GameManagement.Extra.rendering as ex
import GameManagement.singleton as sing
from GameManagement.Utilities.funcs import tuple2Vec2
from GameManagement.locals import *
from pygame.locals import *
from GameManagement.UI.elements import TextLabel, Button, Draggable
from GameManagement.Resources import load_font, load_img
from GameManagement.UI.events import UIEventHandler

import pygame
from pygame.math import Vector2
import math
import os


class TestObject(utils.GameObject):
    def __init__(self, img, name=""):
        super().__init__(image=img, pos=Vector2(0, 0), rotation=0, object_scale=Vector2(1, 1), name=name,
                         components=[])


class TestScene2(smg.Scene):
    def __init__(self):
        super().__init__()

        ui_ev = UIEventHandler([])
        self.add_gameobject(ui_ev, "UI_EVENT_HANDLER")

        test_obj = TestObject(img=load_img(r"resources/test/grid/grid_one.png"), name="test obj")
        self.add_gameobject(test_obj)

        btn = Draggable(Vector2(50, 50), 0, Vector2(1, 1),
                        pygame.transform.scale(load_img("resources/test/grid/dark_grass.png"), (80, 80)), "test_drag",
                        [lambda sc, p, bt: test_obj.rotate(math.pi / 6)], [], anchor=NW)
        lb = TextLabel(Vector2(0, 0), 0, Vector2(1, 1), load_font("resources/test/fonts/remachine.ttf", 45), "button",
                       (200, 200, 200), "test_label", [], anchor=CENTER)
        btn.children.add_gameobject(lb)

        ui_ev.check_objects.append(btn)
        self.add_gameobject(btn)

        camera = ex.Camera(Vector2(0, 0), 0)
        self.register_main_camera(camera)


root = mmg.GameRoot((300, 300), (30, 30, 30), "test game", fps_limit=150,
                    resources_root_path=os.path.dirname(os.path.realpath(__file__)))
root.register(TestScene2())
root.mainloop()
