import threading
import sys

import GameExtensions.inventory as inv
from GameExtensions.UI import *
from GameExtensions.generate_terrain import Terrain, RenderOverTerrain
from GameExtensions.player import Player
from GameExtensions.enemy import Zombie
from GameExtensions.items import *
from GameExtensions.field_objects import Core
from GameExtensions.locals import *
from GameManager.MainLoopManager import GameRoot
from GameManager.resources import *
from GameManager.util import GameObject
from GameManager.locals import VOLUME

root = GameRoot((720, 480), (30, 30, 30), "Defend the cube!", os.path.dirname(os.path.realpath(__file__)),
                Vector2(), 1000)


class Timer(TextLabel):
    def __init__(self, pos: pygame.Vector2, font: pygame.font.Font, color: tuple[int, int, int], name: str):
        super().__init__(pos, 0, font, "0:00", color, name, anchor=NE)
        self.timer = 0
        self.last_sec = 0

    def early_update(self) -> None:
        self.timer += sing.ROOT.delta
        seconds = int(self.timer)
        minutes = seconds // 60
        seconds %= 60
        if self.last_sec != seconds:
            self.set_text(f"{minutes:0=2}:{seconds:0=2}", antialias=True)
            self.last_sec = seconds


class EnemySpawner(GameObject):
    def __init__(self):
        super().__init__(Vector2(0, 0), 0, pygame.Surface((0, 0)), "enemyspawner")
        self.timer = 0
        self.counter = 0
        self.game_time = 0

    def early_update(self) -> None:
        self.timer = max(0, self.timer - sing.ROOT.delta)
        self.game_time += sing.ROOT.delta
        if self.timer == 0:
            if random.random() <= (0.0003 * (self.game_time ** 2) + 6) / 100:
                self.counter += 1
                sing.ROOT.add_gameObject(Zombie(Vector2(random.randint(-1500, 1500), random.randint(-1500, 1500)),
                                                f"Zombie{self.counter}"))
            self.timer = 2


class GameRestarter(GameObject):
    def __init__(self):
        super().__init__(Vector2(0, 0), 0, pygame.Surface((0, 0)), "restarter")
        self.curtain_started = False

    def early_update(self) -> None:
        if self.curtain_started:
            sing.ROOT.game_objects["gr"].surf_mult.add_alpha(120 * sing.ROOT.delta)
            if sing.ROOT.game_objects["gr"].surf_mult.a > 250:
                time = sing.ROOT.game_objects["timer"].timer
                seconds = int(time)
                minutes = seconds // 60
                seconds %= 60
                sing.ROOT.clear_objects()

                game_over_label = TextLabel(Vector2(0, 40), 0, sing.ROOT.global_fonts["title_font"], "GAME OVER",
                                            (200, 200, 200), "game_over", anchor=N)
                gm_over_btn = Button(Vector2(0, 0), 0, load_img("resources/UI/button.png", (60, 32)), "gm_over_btn",
                                     on_mouse_up_func=self.restart, text="menu", font=sing.ROOT.global_fonts["menu_font"],
                                     text_color=(200, 200, 200), anchor=CENTER)
                time_label = TextLabel(Vector2(0, -30), 0, sing.ROOT.global_fonts["arcade_font"],
                                       f"Your time: {minutes:0=2};{seconds:0=2}",
                                       (170, 200, 190), "time_label", anchor=CENTER)
                sing.ROOT.add_gameObject(game_over_label, gm_over_btn, time_label)

        elif sing.ROOT.game_objects["core"].HP == 0:
            gray_thing = BaseUIObject(Vector2(0, 0), 0, load_img("resources/UI/gray_background.png", (720, 480)), "gr",
                                      anchor=CENTER)
            gray_thing.surf_mult.set_alpha(0)
            sing.ROOT.add_gameObject(gray_thing)
            self.curtain_started = True

    def restart(self):
        sing.ROOT.clear_objects()
        main(sing.ROOT.parameters)


class GameLoader(GameObject):
    def __init__(self):
        super().__init__(Vector2(), 0, pygame.Surface((0, 0)), "loader")
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
                load_img("resources/UI/crafting_space.png"),
                load_img("resources/UI/selected_item.png"),
                "inventory",
                root.global_fonts[ITEM_FONT_NAME]
            )

            root.add_gameObject(self.ter,
                                inventory, immediate=True) \
                .add_gameObject(Player(Vector2(-80, 80), 0, "player"), immediate=True) \
                .add_gameObject(RenderOverTerrain(), immediate=True) \
                .add_gameObject(Core(), immediate=True) \
                .game_objects.move_to_end("inventory")

            if "FPS_LABEL" not in sing.ROOT.parameters or sing.ROOT.parameters["FPS_LABEL"]:
                root.add_gameObject(FPS_Label(Vector2(50, 20)))

            root.add_gameObject(HPBar(Vector2(0, -20), S), immediate=True) \
                .add_collidable_object(root.game_objects["player"])

            root.add_gameObject(GameRestarter(), immediate=True)
            root.add_gameObject(EnemySpawner(), immediate=True)
            root.add_gameObject(Timer(Vector2(-50, 30), sing.ROOT.global_fonts["arcade_font"]
                                , (240, 240, 240), "timer"))
            root.game_objects.pop("loader")
            root.game_objects.pop("loading_label")
            root.game_objects.pop("state_label")
            # endregion
            root.setup_priority([
                "gr",
                "inventory",
                "HPBar",
                "dead_label",
                "RenderOverTerrain",
            ])

    def generate_ter(self):
        load_font("resources/test/fonts/square-deal.ttf", FONT_SIZE, global_font=True, name=ITEM_FONT_NAME)
        bs = 32
        biomes = [load_img("resources/environment/terrain/dark_grass.png", (bs, bs)),
                  load_img("resources/environment/terrain/grass.png", (bs, bs))]

        if sing.ROOT.parameters[RAND_SEED]:
            seed = SEED
        else:
            seed = int(sing.ROOT.parameters[CUST_SEED])
        ter = Terrain(seed, (150, 150), biomes, bs, forest_density_scale=1100, forest_size_scale=2000, tree_dens_lim=0.7)
        self.ter = ter


def start_game():
    root.clear_objects()
    root.add_gameObject(GameLoader(), immediate=True)


def main(settings_param=None):
    load_font("resources/fonts/square-deal.ttf", 30, True, "title_font")
    load_font("resources/fonts/square-deal.ttf", 20, True, "menu_font")
    load_font("resources/fonts/arcade.ttf", 24, True, "arcade_font")
    menu_manager = MenuManager()

    load_sound("resources/sounds/button.wav", "button_click")
    btn_sound = sing.ROOT.sounds["button_click"]

    # region ===MAIN MENU===
    main_menu = BaseUIObject(Vector2(0, 0), 0, load_img("resources/blank.png", (720, 480)),
                             "main_menu", anchor=CENTER)

    title_label = TextLabel(Vector2(0, 30), 0, root.global_fonts["title_font"], "Defend the cube!", (200, 200, 200),
                            "title_label", True, N)
    new_game_btn = Button(Vector2(0, -15), 0,
                          load_img("resources/UI/button.png", (168, 32)),
                          "new_game_btn", lambda: start_game(), text="Start a new game",
                          font=root.global_fonts["menu_font"], text_color=(200, 200, 200),
                          anchor=CENTER, on_click_sound=btn_sound)
    settings_btn = Button(Vector2(-42, 30), 0,
                          load_img("resources/UI/button.png", (84, 32)),
                          "settings_btn", lambda: menu_manager.switch_menu("settings"), text="Settings",
                          font=root.global_fonts["menu_font"], text_color=(200, 200, 200),
                          anchor=CENTER, on_click_sound=btn_sound)

    def quit_game():
        pygame.quit()
        sys.exit(0)

    quit_btn = Button(Vector2(42, 30), 0,
                      load_img("resources/UI/button.png", (84, 32)),
                      "quit_btn", quit_game, text="Quit",
                      font=root.global_fonts["menu_font"], text_color=(200, 200, 200),
                      anchor=CENTER, on_click_sound=btn_sound)
    main_menu.children.add_gameobjects(title_label, settings_btn, quit_btn, new_game_btn)
    # endregion

    # region ===SETTINGS===
    settings = BaseUIObject(Vector2(0, 0), 0, load_img("resources/blank.png", (720, 480)),
                            "settings", anchor=CENTER)

    title_label = TextLabel(Vector2(0, 30), 0, root.global_fonts["title_font"], "Settings", (200, 200, 200),
                            "title_label", True, N)

    volume_label = TextLabel(Vector2(-160, 105), 0, sing.ROOT.global_fonts["menu_font"], "Volume",
                             (190, 190, 190), "volume_label", anchor=N)

    default_vol = 0.7 if settings_param is None else settings_param[VOLUME]
    sing.ROOT.set_parameter(VOLUME, default_vol)
    volume_slider = Slider(Vector2(0, 105), load_img("resources/UI/bar.png", (192, 8)),
                           load_img("resources/UI/circle.png"), "volume_slider",
                           on_slider_release_func=lambda b: sing.ROOT.modify_volume(sing.ROOT.parameters[VOLUME]),
                           anchor=N, step=0.05, init_value=default_vol)

    fps_default = False if settings_param is None else settings_param["FPS_LABEL"]
    sing.ROOT.set_parameter("FPS_LABEL", fps_default)
    fps_label = TextLabel(Vector2(-160, 145), 0, sing.ROOT.global_fonts["menu_font"], "Show FPS",
                          (190, 190, 190), "fps_label", anchor=N)

    fps_check = CheckBox(Vector2(0, 145), load_img("resources/UI/check_box.png"),
                         load_img("resources/UI/check_mark.png"), "fps_check",
                         on_check_func=lambda b: sing.ROOT.set_parameter("FPS_LABEL", b), anchor=N,
                         default_state=fps_default)

    seed_inp_label = TextLabel(Vector2(-160, 225), 0, sing.ROOT.global_fonts["menu_font"], "Custom seed",
                               (190, 190, 190), "seed_inp_label", anchor=N)

    default = "123" if settings_param is None else settings_param[CUST_SEED]
    sing.ROOT.set_parameter(CUST_SEED, default)
    seed_box = TextBox(Vector2(0, 225), load_img("resources/UI/textbox.png", (192, 16)),
                       sing.ROOT.global_fonts["menu_font"], (100, 120, 200),
                       "seed_box", on_new_text_typed=lambda txt: sing.ROOT.set_parameter(CUST_SEED, txt),
                       default_text=default, allowed_chars="0123456789", anchor=N)

    seed_bool_label = TextLabel(Vector2(-160, 185), 0, sing.ROOT.global_fonts["menu_font"], "Randomize seed",
                                (190, 190, 190), "seed_bool_label", anchor=N)

    randomize = True if settings_param is None else settings_param[RAND_SEED]
    sing.ROOT.set_parameter(RAND_SEED, randomize)

    def on_check(b):
        sing.ROOT.set_parameter(RAND_SEED, b)
        seed_box.set_enabled(not b)
        seed_inp_label.set_enabled(not b)

    on_check(randomize)

    seed_check = CheckBox(Vector2(0, 185), load_img("resources/UI/check_box.png"),
                          load_img("resources/UI/check_mark.png"),
                          "seed_bool_check", on_check_func=on_check,
                          anchor=N, default_state=randomize)

    back = Button(Vector2(0, 135), 0,
                  load_img("resources/UI/button.png", (60, 32)),
                  "back_btn", lambda: menu_manager.switch_menu("main_menu"), text="Back",
                  font=root.global_fonts["menu_font"], text_color=(200, 200, 200),
                  anchor=CENTER, on_click_sound=btn_sound)

    settings.children.add_gameobjects(title_label, volume_label, volume_slider, fps_label, fps_check,
                                      seed_bool_label, seed_check, seed_inp_label, seed_box, back)

    # endregion

    menu_manager.add_menus(main_menu, settings)
    menu_manager.switch_menu("main_menu")
    root.add_gameObject(menu_manager)

    root.mainloop()


if __name__ == "__main__":
    main()
