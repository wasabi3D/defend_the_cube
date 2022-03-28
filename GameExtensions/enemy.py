from GameManager.util import GameObject
import GameManager.singleton as sing

from GameExtensions.util import get_grid_pos, get_chunk_pos, PathFinder2NextChunk, PathFinderNoObstacles
from GameExtensions.util import grid_pos2world_pos, PathFinder2Pos
from GameExtensions.locals import N, W, S, E, CHUNK_SIZE, DIRS

import pygame
from pygame.math import Vector2

from typing import Optional

import time

class TestEnemy(GameObject):
    def __init__(self, pos: Vector2, image: pygame.Surface, name: str):
        super().__init__(pos, 0, image, name)
        self.objectives: list[Vector2] = [self.get_real_pos()]
        self.last_chunk: Optional[Vector2] = None
        self.chunk_path = PathFinderNoObstacles(get_chunk_pos(self.get_real_pos()),
                                                get_chunk_pos(sing.ROOT.game_objects["player"].get_real_pos()))
        self.check_pos = self.get_real_pos().copy()
        self.last_checked = time.time()
        self.map = sing.ROOT.game_objects["terrain"].over_terrain

    def update(self) -> None:
        player_pos = sing.ROOT.game_objects["player"].get_real_pos()
        dist = (self.get_real_pos().x - player_pos.x) ** 2 + (self.get_real_pos().y - player_pos.y) ** 2
        if get_chunk_pos(self.get_real_pos()) != self.last_chunk or (len(self.objectives) == 0 and dist > 50):
            self.calculate_path(player_pos)
        if time.time() - self.last_checked > 5:
            if (self.get_real_pos() - self.check_pos).magnitude_squared() < 1:
                print("as")
                grid_pos = get_grid_pos(self.get_real_pos())
                for d in DIRS:
                    obj = self.map[int(grid_pos.y + d[0])][int(grid_pos.x + d[1])]
                    if obj is None:
                        continue
                    sing.ROOT.remove_collidable_object(obj)
                    self.map[int(grid_pos.y + d[0])][int(grid_pos.x + d[1])] = None

                self.objectives.clear()
                self.calculate_path(player_pos)
            self.check_pos = self.get_real_pos().copy()
            self.last_checked = time.time()

        if len(self.objectives) == 0:
            return

        # print(self.get_real_pos())

        mov_vec = (self.objectives[0] - self.get_real_pos())
        if mov_vec.length_squared() > 0:
            mov_vec.normalize_ip()
        dx = mov_vec.x
        dy = mov_vec.y

        rp = self.get_real_pos()
        dx_tmp_rect = self.image.get_rect(center=rp + Vector2(dx, 0))
        dy_tmp_rect = self.image.get_rect(center=rp + Vector2(0, dy))
        if sing.ROOT.is_colliding(dx_tmp_rect, exclude=self.name) != -1:
            dx = 0
        if sing.ROOT.is_colliding(dy_tmp_rect, exclude=self.name) != -1:
            dy = 0

        self.translate(Vector2(dx, dy))
        diff_x = abs(self.get_real_pos().x - self.objectives[0].x)
        diff_y = abs(self.get_real_pos().y - self.objectives[0].y)
        if diff_x < 5 and diff_y < 5:
            self.objectives.pop(0)

    def calculate_path(self, player_pos):
        self.last_chunk = get_chunk_pos(self.get_real_pos())
        self.chunk_path.current = self.last_chunk
        self.chunk_path.target = get_chunk_pos(player_pos)
        nxt_chunk = self.chunk_path.get_next()
        # self.chunk_path.current = nxt_chunk
        chunk_diff = nxt_chunk - self.last_chunk
        if chunk_diff == Vector2(0, -1):
            d = N
        elif chunk_diff == Vector2(0, 1):
            d = S
        elif chunk_diff == Vector2(1, 0):
            d = E
        elif chunk_diff == Vector2(-1, 0):
            d = W
        else:
            pf = PathFinder2Pos(get_grid_pos(self.get_real_pos()),
                                get_grid_pos(player_pos))
            self.objectives += list(map(lambda pos: grid_pos2world_pos(pos), pf.calculate()))
            return
        chunk_topleft = self.last_chunk * CHUNK_SIZE
        pf = PathFinder2NextChunk(get_grid_pos(self.get_real_pos()), d, chunk_topleft + Vector2(-2, -2),
                                  chunk_topleft + Vector2(CHUNK_SIZE, CHUNK_SIZE) + Vector2(2, 2))
        self.objectives += list(map(lambda pos: grid_pos2world_pos(pos), pf.calculate()))
