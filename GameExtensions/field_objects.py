from __future__ import annotations  # Avoid circular import

import typing

import GameExtensions.generate_terrain
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
    def __init__(self, pos: Vector2, image: pygame.Surface, name: str, rotation=0):
        super().__init__(pos, rotation, image, name)
        self.terrain: Terrain = sing.ROOT.game_objects["terrain"]
        if not isinstance(self.terrain, GameExtensions.generate_terrain.Terrain):
            raise TypeError("terrain is not an instance of Terrain")

        grid_pos = self.get_grid_pos()
        self.translate(self.terrain.get_real_pos() + grid_pos * self.terrain.block_px_size
                       - tuple2Vec2(self.terrain.size) * self.terrain.block_px_size / 2, additive=False)
        if self.terrain.over_terrain[int(grid_pos.y)][int(grid_pos.x)] is None and\
                sing.ROOT.is_colliding(self.image.get_rect(center=self.get_real_pos())) == -1:
            self.terrain.over_terrain[int(grid_pos.y)][int(grid_pos.x)] = self
            sing.ROOT.add_collidable_object(self)

        # print(grid_pos)
        # print(self.get_real_pos())

    def get_grid_pos(self) -> Vector2:
        map_pos = self.terrain.get_real_pos()
        dim_per_block = self.terrain.block_px_size
        rel_pos = self.get_real_pos() - map_pos + Vector2(self.terrain.block_px_size, self.terrain.block_px_size) / 2
        rel_pos = rel_pos // dim_per_block
        rel_pos += Vector2(len(self.terrain.over_terrain[0]) // 2, len(self.terrain.over_terrain) // 2)
        return rel_pos


class WoodBlock(Placeable):
    def __init__(self, pos: Vector2):
        super().__init__(pos, load_img("resources/items/wood_block.png"), "wood_block")




