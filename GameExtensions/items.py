from GameExtensions.inventory import InventoryObject
from GameManager.resources import load_img
import pygame


class Apple(InventoryObject):
    SIZE = (32, 32)

    def __init__(self, n: int, font: pygame.font.Font):
        super().__init__("apple", load_img("resources/items/apple.png", Apple.SIZE), n, font)

    def copy(self):
        return Apple(self.n, self.font)

    def on_use(self):
        print("apple")
