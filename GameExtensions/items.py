from GameExtensions.inventory import InventoryObject
from GameManager.resources import load_img
from GameExtensions.locals import ITEM_SPRITE_SIZE
import pygame


class Apple(InventoryObject):
    def __init__(self, n: int, font: pygame.font.Font):
        super().__init__("apple", load_img("resources/items/apple.png", ITEM_SPRITE_SIZE), n, font)

    def copy(self):
        return Apple(self.n, self.font)

    def on_use(self):
        print("apple")


class Log(InventoryObject):
    def __init__(self, n: int, font: pygame.font.Font):
        super().__init__("log", load_img("resources/items/log.png", ITEM_SPRITE_SIZE), n, font)

    def copy(self):
        return Log(self.n, self.font)

    def on_use(self):
        print("log")


class Stone(InventoryObject):
    def __init__(self, n: int, font: pygame.font.Font):
        super().__init__("stone", load_img("resources/items/stone.png", ITEM_SPRITE_SIZE), n, font)

    def copy(self):
        return Stone(self.n, self.font)

    def on_use(self):
        print("stone")
