from __future__ import annotations  # Avoid circular import

import typing

import GameExtensions.generate_terrain
from GameExtensions.util import get_grid_pos, HPBar

from GameManager.util import GameObject
import GameManager.singleton as sing
from GameManager.resources import load_img
from GameManager.util import tuple2Vec2

if typing.TYPE_CHECKING:
    from GameExtensions.generate_terrain import Terrain

from abc import ABCMeta

import pygame
from pygame.math import Vector2


class Placeable(GameObject, metaclass=ABCMeta):
    """
    Une classe qui généralise tous les objets qu'on peut placer sur le terrain
    """
    def __init__(self, pos: Vector2, image: pygame.Surface, name: str, rotation=0, block_health=10):
        """

        :param pos: La position initiale de l'objet. La valeur par défaut est pygame.Vector2(0, 0).
        :param rotation: La rotation en radian initiale de l'objet. La valeur par défaut est 0.
        :param image: L'image de l'objet initiale.
        :param name: Le nom de l'objet.
        :param rotation: La rotation initiale
        """
        super().__init__(pos, rotation, image, name)
        self.terrain: Terrain = sing.ROOT.game_objects["terrain"]
        if not isinstance(self.terrain, GameExtensions.generate_terrain.Terrain):
            raise TypeError("terrain is not an instance of Terrain")

        self.grid_pos = get_grid_pos(self.get_real_pos())
        self.translate(self.terrain.get_real_pos() + self.grid_pos * self.terrain.block_px_size
                       - tuple2Vec2(self.terrain.size) * self.terrain.block_px_size / 2, additive=False)
        self.block_health = block_health

    def register(self) -> bool:
        """
        Essaye de placer le block si possible

        :return: True s'il reussit à placer False sinon
        """
        if self.terrain.over_terrain[int(self.grid_pos.y)][int(self.grid_pos.x)] is None and\
                sing.ROOT.is_colliding(self.image.get_rect(center=self.get_real_pos())) == -1:
            self.terrain.over_terrain[int(self.grid_pos.y)][int(self.grid_pos.x)] = self
            sing.ROOT.add_collidable_object(self)
            return True
        return False

    def get_grid_pos(self) -> Vector2:
        """
        Calcule la position(index) du block sur la map

        :return: La position en Vector2
        """
        map_pos = self.terrain.get_real_pos()
        dim_per_block = self.terrain.block_px_size
        rel_pos = self.get_real_pos() - map_pos + Vector2(self.terrain.block_px_size, self.terrain.block_px_size) / 2
        rel_pos //= dim_per_block
        rel_pos += Vector2(len(self.terrain.over_terrain[0]) // 2, len(self.terrain.over_terrain) // 2)
        return rel_pos

    def damage(self, amount: int):
        self.block_health -= amount
        if self.block_health <= 0:
            self.terrain.over_terrain[int(self.grid_pos.y)][int(self.grid_pos.x)] = None
            sing.ROOT.remove_collidable_object(self)


class Core(Placeable):
    """
    L'objet que le joueur doit défendre par les ennemis
    """
    def __init__(self):
        super().__init__(Vector2(0, 0), load_img("resources/core.png", (64, 64)), "core")
        self.children.add_gameobject(HPBar(Vector2(0, -40), size=(120, 12)))
        self.maxHP = 200
        self.HP = self.maxHP
        self.register()

    def early_update(self) -> None:
        super().early_update()
        self.children["HPBar"].prop = self.HP / self.maxHP

    def damage(self, amount):
        """
        Fonction pour donner du dégat au core

        :param amount: La quantité du dégat
        """
        self.HP = max(self.HP - amount, 0)


class WoodBlock(Placeable):
    """
    La classe pour les blocks en bois
    """
    def __init__(self, pos: Vector2):
        """
        :param pos: La position sur la map
        """
        super().__init__(pos, load_img("resources/items/wood_block.png"), "wood_block", block_health=50)


class StoneBlock(Placeable):
    """
    La classe pour les blocks en pierre
    """
    def __init__(self, pos: Vector2):
        """
        :param pos: La position sur la map
        """
        super().__init__(pos, load_img("resources/items/stone_block.png"), "stone_block", block_health=65)


