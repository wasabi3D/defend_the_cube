from GameExtensions.inventory import InventoryObject
from GameExtensions.locals import *

from GameManager.resources import load_img
import GameManager.singleton as sing
from GameManager.util import GameObject

import pygame
from pygame.math import Vector2

from typing import Optional


class Apple(InventoryObject):
    """
    La classe pour définir une pomme
    """
    def __init__(self, n: int, font: pygame.font.Font):
        """

        :param n: Nombre de pommes
        :param font: Police pour afficher le nombre des pommes
        """
        super().__init__("apple", load_img("resources/items/apple.png", ITEM_SPRITE_SIZE), n, font)
        self.tag.append(SLASHABLE)

    def copy(self):
        return Apple(self.n, self.font)

    def on_use(self):
        pass


class Log(InventoryObject):
    """
    La classe pour définir du bois
    """
    def __init__(self, n: int, font: pygame.font.Font):
        super().__init__("log", load_img("resources/items/log.png", ITEM_SPRITE_SIZE), n, font)

    def copy(self):
        return Log(self.n, self.font)

    def on_use(self):
        pass


class Stone(InventoryObject):
    """
    La classe pour définir de la roche
    """
    def __init__(self, n: int, font: pygame.font.Font):
        super().__init__("stone", load_img("resources/items/stone.png", ITEM_SPRITE_SIZE), n, font)

    def copy(self):
        return Stone(self.n, self.font)

    def on_use(self):
        pass


class WoodBlockItem(InventoryObject):
    """
    La classe pour définir l'item des blocks de bois
    """
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
            self.n -= 1  # There's a problem with this thing


class Weapon(InventoryObject):
    """
    Une classe pour généraliser les item des armes
    """
    def __init__(self, name: str, img: pygame.Surface, n: int, damage: int):
        super().__init__(name, img, n)
        self.damage = damage
        self.tag.append(SLASHABLE)


class Sword(Weapon):
    """
    La classe pour définir l'item de l'épée
    """
    def __init__(self, n: int):
        super().__init__("iron_sword", load_img("resources/items/iron_sword.png"), n, 10)

    def copy(self):
        return WoodBlockItem(self.n, self.font)

    def on_use(self):
        pass


class MagicBullet(GameObject):
    """
    La boule magique shooté quand le joueur utilise un livre
    """
    SPEED = 180
    DIR_CORRECTION = 0.8
    TARGET_DETECT_DISTANCE = 140
    LIFE_DURATION = 5
    DAMAGE = 10

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
                if gm.get_real_pos().distance_squared_to(self.get_real_pos()) <= MagicBullet.TARGET_DETECT_DISTANCE ** 2:
                    self.target = gm
                    break

        else:
            if self.image.get_rect(center=self.get_real_pos()).colliderect(
                    self.target.image.get_rect(center=self.target.get_real_pos())):
                sing.ROOT.remove_object(self)
                self.target.get_damage(MagicBullet.DAMAGE, Vector2(0, 0))
                return
            self.direction += (self.target.get_real_pos() - self.get_real_pos()).normalize() * MagicBullet.DIR_CORRECTION
            self.direction.normalize_ip()


class Book(Weapon):
    """
    La classe pour définir le livre pour tirer des boules magiques
    """
    def __init__(self):
        super().__init__("book", load_img("resources/items/book.png"), 1, 10)
        self.tag.append(DONT_SLASH)
        self.player = sing.ROOT.game_objects["player"]

    def copy(self):
        return Book()

    def on_use(self):
        sing.ROOT.objects2be_added.append(MagicBullet(self.player.get_real_pos(), self.player.get_direction_vec()))
