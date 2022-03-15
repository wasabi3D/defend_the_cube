from GameManager.MainLoopManager import GameRoot
from GameManager.resources import load_img, load_font
from GameManager.util import GameObject
from GameExtensions.UI import FPS_Label, HPBar
from GameExtensions.items import Apple
import GameExtensions.inventory as inv
from GameExtensions.locals import *
import GameManager.singleton as sing
import pygame
import random
from pygame.math import Vector2
from pygame.locals import *
from GameExtensions.generate_terrain import Terrain
from GameExtensions.player import Player
import os


class TestObject(GameObject):
    def __init__(self, pos: Vector2, rotation: float, image: pygame.Surface, name: str):
        super().__init__(pos, rotation, image, name)

    def on_mouse_down(self, button: int):
        print("cc")

    def on_mouse_rect_exit(self):
        print("exit")

    def get_collision_rect(self) -> pygame.Rect:
        a = super().get_collision_rect()
        return a


class RenderOverTerrain(GameObject):
    def __init__(self):
        super().__init__(Vector2(0, 0), 0, pygame.Surface((0, 0)), "RenderOverTerrain")

    def blit(self, screen: pygame.Surface) -> None:
        sing.ROOT.game_objects["terrain"].blit_over_terrain(screen)


if __name__ == "__main__":
    root = GameRoot((720, 480), (30, 30, 30), "test game", os.path.dirname(os.path.realpath(__file__)),
                    Vector2(0, 0), 1000)

    bs = 32
    biomes = [load_img("resources/environment/terrain/dark_grass.png", (bs, bs)),
              load_img("resources/environment/terrain/grass.png", (bs, bs))]
    ter = Terrain(500, (150, 150), biomes, bs, forest_density_scale=1100, forest_size_scale=2000, tree_dens_lim=0.7)

    root.add_gameObject(ter)
    root.add_gameObject(Player(Vector2(0, 0), 0, "player"))
    root.add_gameObject(TestObject(Vector2(100, 200), 0, load_img("resources/test/grid/grid_one.png"), "yay"))
    root.add_collidable_object(root.game_objects["yay"])
    root.add_gameObject(RenderOverTerrain())
    root.add_gameObject(FPS_Label(Vector2(50, 20)))
    root.add_gameObject(HPBar(Vector2(0, -20), S))

    inventory = inv.Inventory(
        (8, 6), Vector2(40, 40),
        load_img("resources/UI/inventory.png"),
        load_img("resources/UI/hotbar.png"), load_img("resources/UI/selected_item.png"),
        "inventory",
        load_font("resources/test/fonts/square-deal.ttf", FONT_SIZE)
    )
    inventory.add_obj("sand", load_img("resources/test/grid/grid_one.png"), 5)
    inventory.add_obj_at_pos((1, 1), "sand", load_img("resources/test/grid/grid_one.png"), 3)
    inventory.add_obj("frog", load_img("resources/test/frog.png"), 10)
    inventory.add_obj_ins(Apple(10, inventory.font))
    inventory.add_obj_ins_at_place((4, 4), Apple(6, inventory.font))
    inventory.add_obj_ins(Apple(5, inventory.font))
    inventory.add_obj_at_pos((2, 2), "frog", load_img("resources/test/frog.png"), 95)
    root.add_gameObject(inventory)
    # root.add_gameObject(TestObject(Vector2(0, 0), 0, load_img("resources/test/grid/grid_one.png"), "test_obj"))
    # root.add_gameObject(TextLabel(Vector2(30, 30), 0, load_font("resources/test/fonts/remachine.ttf", 25),
    #                               "hello world", (200, 200, 200), "test_label", anchor=CENTER))

    root.mainloop()
