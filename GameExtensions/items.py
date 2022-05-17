from GameExtensions.locals import *

from GameManager.resources import load_img
import GameManager.singleton as sing
from GameManager.util import GameObject

import pygame
from pygame.math import Vector2

from typing import Optional


# Classe pour les objets d'inventaire
class InventoryObject:
    def __init__(self, name: str, img: pygame.Surface, n: int, font: Optional[pygame.font.Font] = None):
        self.name = name
        self.img = img
        self.n = n
        if font is None:
            font = sing.ROOT.global_fonts[ITEM_FONT_NAME]
        self.font = font
        self.n_img = font.render(str(self.n), False, NUMBER_COLOR)
        self.max_n = SPE_OBJ[self.name] if self.name in SPE_OBJ else MAX_OBJ
        self.tag: list[str] = []

    def get_img(self) -> pygame.Surface:
        return self.img

    def get_name(self) -> str:
        return self.name

    def get_n(self) -> int:
        return self.n

    def get_n_img(self) -> pygame.Surface:
        return self.n_img

    def set_n(self, n: int):
        self.n = n
        self.n_img = self.font.render(str(self.n), False, NUMBER_COLOR)

    def add_n(self, n: int):
        tmp = self.n
        self.n = min(self.n + n, self.max_n)
        self.n_img = self.font.render(str(self.n), False, NUMBER_COLOR)
        return max(tmp + n - self.max_n, 0)

    def remove_one(self):
        self.n -= 1
        self.n_img = self.font.render(str(self.n), False, NUMBER_COLOR)
        if self.n <= 0:
            return False
        return True

    def copy(self):
        return InventoryObject(self.name, self.img, self.n, self.font)

    def on_use(self):
        return True


class Apple(InventoryObject):
    """
    La classe pour définir une pomme
    """
    def __init__(self, n: int, font: pygame.font.Font):
        """

        :param n: Nombre de pommes
        :param font: Police pour afficher le nombre des pommes
        """
        super().__init__(APPLE, load_img("resources/items/apple.png", ITEM_SPRITE_SIZE), n, font)
        self.tag.append(SLASHABLE)

    def copy(self):
        return Apple(self.n, self.font)

    def on_use(self):
        player = sing.ROOT.game_objects["player"]
        player.hp += 20
        return self.remove_one()


class Log(InventoryObject):
    """
    La classe pour définir du bois
    """
    def __init__(self, n: int, font: pygame.font.Font):
        super().__init__(LOG, load_img("resources/items/log.png", ITEM_SPRITE_SIZE), n, font)

    def copy(self):
        return Log(self.n, self.font)


class Stone(InventoryObject):
    """
    La classe pour définir de la roche
    """
    def __init__(self, n: int, font: pygame.font.Font):
        super().__init__("stone", load_img("resources/items/stone.png", ITEM_SPRITE_SIZE), n, font)

    def copy(self):
        return Stone(self.n, self.font)


class IronOre(InventoryObject):
    """
    La classe pour définir du fer
    """
    def __init__(self, n: int, font: pygame.font.Font):
        super().__init__(IRON_ORE, load_img("resources/items/iron_ore.png", ITEM_SPRITE_SIZE), n, font)

    def copy(self):
        return IronOre(self.n, self.font)


class WoodBlockItem(InventoryObject):
    """
    La classe pour définir l'item des blocks de bois
    """
    def __init__(self, n: int, font: pygame.font.Font):
        super().__init__(WOOD_BLOCK, load_img("resources/items/wood_block.png", ITEM_SPRITE_SIZE), n, font)
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
            block = WoodBlock(pos)
            if block.register():
                return self.remove_one()
        return True


class StoneBlockItem(InventoryObject):
    """
    La classe pour définir l'item des blocks de pierre
    """
    def __init__(self, n: int, font: pygame.font.Font):
        super().__init__(STONE_BLOCK, load_img("resources/items/stone_block.png", ITEM_SPRITE_SIZE), n, font)
        self.tag.append(HOLDABLE)
        self.tag.append(PLACEABLE)

    def copy(self):
        return WoodBlockItem(self.n, self.font)

    def on_use(self):
        from GameExtensions.field_objects import StoneBlock
        pl = sing.ROOT.game_objects["player"]
        holding = pl.children["item_holder"].children
        if len(holding) > 0:
            pos = tuple(holding.values())[0].get_real_pos()
            block = StoneBlock(pos)
            if block.register():
                return self.remove_one()
        return True


class Weapon(InventoryObject):
    """
    Une classe pour généraliser les item des armes
    """
    def __init__(self, name: str, img: pygame.Surface, n: int, damage: int):
        super().__init__(name, img, n)
        self.damage = damage
        self.tag.append(SLASHABLE)

    def on_use(self):
        return True


class Sword(Weapon):
    """
    La classe pour définir l'item de l'épée
    """
    def __init__(self, *args):
        super().__init__(IRON_SWORD, load_img("resources/items/iron_sword.png", ITEM_SLOT_SIZE), 1, 10)

    def copy(self):
        return Sword(self.n, self.font)


class GoldenSword(Weapon):
    """ Meilleur epee"""
    def __init__(self, *args):
        super().__init__(GOLDEN_SWORD, load_img("resources/items/golden_sword.png", ITEM_SLOT_SIZE), 1, 30)

    def copy(self):
        return GoldenSword()


class MagicBullet(GameObject):
    """
    La boule magique shooté quand le joueur utilise un livre
    """
    SPEED = 180
    DIR_CORRECTION = 0.8
    TARGET_DETECT_DISTANCE = 140
    LIFE_DURATION = 5
    DAMAGE = 5

    def __init__(self, pos: Vector2, direction: Vector2):
        super().__init__(pos, 0, load_img("resources/player/magic_bullet.png", (16, 16)),
                         f"mb{pygame.time.get_ticks()}")
        self.direction = direction
        self.target: Optional[GameObject] = None
        self.timer = 0

    def update(self) -> None:
        self.translate(self.direction * MagicBullet.SPEED * sing.ROOT.delta)

        if self.target is None:
            self.timer += sing.ROOT.delta
            if self.timer > MagicBullet.LIFE_DURATION:
                sing.ROOT.remove_object(self)
            for gm in sing.ROOT.get_obj_list_by_tag(ENEMY):
                if gm.get_real_pos().distance_squared_to(self.get_real_pos()) <= \
                        MagicBullet.TARGET_DETECT_DISTANCE ** 2:
                    self.target = gm
                    break

        else:
            if self.image.get_rect(center=self.get_real_pos()).colliderect(
                    self.target.image.get_rect(center=self.target.get_real_pos())):
                sing.ROOT.remove_object(self)
                self.target.get_damage(MagicBullet.DAMAGE, Vector2(0, 0))
                return
            self.direction += (self.target.get_real_pos() - self.get_real_pos()).normalize() * \
                              MagicBullet.DIR_CORRECTION
            self.direction.normalize_ip()


class Book(Weapon):
    """
    La classe pour définir le livre pour tirer des boules magiques
    """
    def __init__(self, *args):
        super().__init__(BOOK, load_img("resources/items/book.png", ITEM_SLOT_SIZE), 1, 10)
        self.tag.append(DONT_SLASH)
        self.player = sing.ROOT.game_objects["player"]

    def copy(self):
        return Book()

    def on_use(self):
        sing.ROOT.objects2be_added.append(MagicBullet(self.player.get_real_pos(), self.player.get_direction_vec()))
        return True


def get_recipes() -> \
        dict[tuple[tuple[str, str, str], tuple[str, str, str], tuple[str, str, str]], tuple]:
    """ Nous donne toutes les combinaisons possibles dans le menu de craft"""
    return {
        ((LOG, LOG, EMPTY),
         (LOG, LOG, EMPTY),
         (EMPTY, EMPTY, EMPTY)): (WoodBlockItem, 2),

        ((STONE, STONE, STONE),
         (EMPTY, EMPTY, EMPTY),
         (EMPTY, EMPTY, EMPTY)): (Apple, 1),

        ((EMPTY, EMPTY, IRON_ORE),
         (EMPTY, IRON_ORE, EMPTY),
         (LOG, EMPTY, EMPTY)): (Sword, 1),

        ((APPLE, APPLE, APPLE),
         (APPLE, APPLE, APPLE),
         (APPLE, APPLE, APPLE)): (Book, 1),

        ((STONE, IRON_SWORD, STONE),
         (IRON_SWORD, STONE, IRON_SWORD),
         (STONE, IRON_SWORD, STONE)): (GoldenSword, 1),

        ((STONE, STONE, EMPTY),
         (STONE, STONE, EMPTY),
         (EMPTY, EMPTY, EMPTY)): (StoneBlockItem, 2)

    }
