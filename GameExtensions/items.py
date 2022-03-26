from GameExtensions.inventory import InventoryObject
from GameManager.resources import load_img
from GameExtensions.locals import ITEM_SPRITE_SIZE, HOLDABLE, PLACEABLE
import GameManager.singleton as sing
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


class WoodBlockItem(InventoryObject):
    def __init__(self, n: int, font: pygame.font.Font):
        super().__init__("wood_block", load_img("resources/items/wood_block.png"), n, font)
        self.tag.append(HOLDABLE)
        self.tag.append(PLACEABLE)

    def copy(self):
        return WoodBlockItem(self.n, self.font)

    def on_use(self):
        from GameExtensions.field_objects import WoodBlock
        pl = sing.ROOT.game_objects["player"]
        holding = pl.children["item_holder"].children
        if len(holding) > 0:
            pos = tuple(holding.values())[0].get_real_pos()
            WoodBlock(pos)

