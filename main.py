import os
import threading
import time
import sys
from typing import Optional

import pygame
from pygame.math import Vector2

import GameExtensions.inventory as inv
from GameExtensions.UI import FPS_Label, HPBar, Button, TextLabel, BaseUIObject, MenuManager
from GameExtensions.generate_terrain import Terrain, RenderOverTerrain
from GameExtensions.locals import *
from GameExtensions.player import Player
from GameExtensions.enemy import Zombie
from GameExtensions.items import *
from GameManager.MainLoopManager import GameRoot
from GameManager.resources import load_img, load_font
from GameManager.util import GameObject

root = GameRoot((720, 480), (30, 30, 30), "Game", os.path.dirname(os.path.realpath(__file__)),
                Vector2(0, 0), 1000)


class GameLoader(GameObject):
    def __init__(self):
        super().__init__(Vector2(0, 0), 0, pygame.Surface((0, 0)), "loader")
        root.add_gameObject(TextLabel(Vector2(0, -25), 0, root.global_fonts["menu_font"], "Loading...", (200, 200, 200),
                                      "loading_label", anchor=S),
                            TextLabel(Vector2(0, -50), 0, root.global_fonts["menu_font"], "Generating terrain...",
                                      (200, 200, 200), "state_label", anchor=S))
        self.ter: Optional[Terrain] = None

        ter_gen_th = threading.Thread(target=self.generate_ter)
        ter_gen_th.start()

    def early_update(self) -> None:
        if self.ter is not None:
            # region Generate objects
            lb: TextLabel = root.game_objects["state_label"]
            if lb.text != "Initializing...":
                lb.set_text("Initializing...")
                return
            inventory = inv.Inventory(
                (8, 6), Vector2(40, 40),
                load_img("resources/UI/inventory.png"),
                load_img("resources/UI/hotbar.png"),
                load_img("resources/UI/selected_item.png"),
                "inventory",
                root.global_fonts[ITEM_FONT_NAME]
            )

            root.add_gameObject(self.ter,
                                inventory) \
                .add_gameObject(Player(Vector2(0, 0), 0, "player")) \
                .add_gameObject(Zombie(Vector2(-50, 100), "zombie")) \
                .add_gameObject(RenderOverTerrain()) \
                .game_objects.move_to_end("inventory")

            root.add_gameObject(FPS_Label(Vector2(50, 20)),
                                HPBar(Vector2(0, -20), S)) \
                .add_collidable_object(root.game_objects["player"])

            inventory.add_obj("sand", load_img("resources/test/grid/grid_one.png"), 5)
            inventory.add_obj_at_pos((2, 2), "frog", load_img("resources/test/frog.png"), 95)
            inventory.add_obj_ins(WoodBlockItem(10, inventory.font))
            inventory.add_obj_ins(Sword(1))
            inventory.add_obj_ins(Book())
            time.sleep(2)
            root.game_objects.pop("loader")
            root.game_objects.pop("loading_label")
            root.game_objects.pop("state_label")
            # endregion

    def generate_ter(self):
        load_font("resources/test/fonts/square-deal.ttf", FONT_SIZE, global_font=True, name=ITEM_FONT_NAME)
        bs = 32
        biomes = [load_img("resources/environment/terrain/dark_grass.png", (bs, bs)),
                  load_img("resources/environment/terrain/grass.png", (bs, bs))]
        ter = Terrain(500, (150, 150), biomes, bs, forest_density_scale=1100, forest_size_scale=2000, tree_dens_lim=0.7)
        self.ter = ter


def start_game():
    root.clear_objects()
    root.add_gameObject(GameLoader())


def main():
    load_font("resources/fonts/square-deal.ttf", 30, True, "title_font")
    load_font("resources/fonts/square-deal.ttf", 20, True, "menu_font")
    menu_manager = MenuManager()

    # region ===MAIN MENU===
    main_menu = BaseUIObject(Vector2(0, 0), 0, load_img("resources/blank.png", (720, 480)),
                             "main_menu", anchor=CENTER)
    title_label = TextLabel(Vector2(0, 30), 0, root.global_fonts["title_font"], "Game title here", (200, 200, 200),
                            "title_label", True, N)
    new_game_btn = Button(Vector2(0, -15), 0,
                          load_img("resources/UI/button.png", (168, 32)),
                          "new_game_btn", lambda: start_game(), text="Start a new game",
                          font=root.global_fonts["menu_font"], text_color=(200, 200, 200),
                          anchor=CENTER)
    settings_btn = Button(Vector2(-42, 30), 0,
                          load_img("resources/UI/button.png", (84, 32)),
                          "settings_btn", lambda: menu_manager.switch_menu("settings"), text="Settings",
                          font=root.global_fonts["menu_font"], text_color=(200, 200, 200),
                          anchor=CENTER)

    def quit_game():
        pygame.quit()
        sys.exit()

    quit_btn = Button(Vector2(42, 30), 0,
                      load_img("resources/UI/button.png", (84, 32)),
                      "quit_btn", quit_game, text="Quit",
                      font=root.global_fonts["menu_font"], text_color=(200, 200, 200),
                      anchor=CENTER)
    main_menu.children.add_gameobjects(title_label, settings_btn, quit_btn, new_game_btn)
    # endregion

    # region ===SETTINGS===
    settings = BaseUIObject(Vector2(0, 0), 0, load_img("resources/blank.png", (720, 480)),
                            "settings", anchor=CENTER)

    title_label = TextLabel(Vector2(0, 30), 0, root.global_fonts["title_font"], "Settings", (200, 200, 200),
                            "title_label", True, N)

    back = Button(Vector2(0, 135), 0,
                  load_img("resources/UI/button.png", (60, 32)),
                  "back_btn", lambda: menu_manager.switch_menu("main_menu"), text="Back",
                  font=root.global_fonts["menu_font"], text_color=(200, 200, 200),
                  anchor=CENTER)

    settings.children.add_gameobjects(title_label, back)

    # endregion

    menu_manager.add_menus(main_menu, settings)
    menu_manager.switch_menu("main_menu")
    root.add_gameObject(menu_manager)

    root.mainloop()


if __name__ == "__main__":
    main()
