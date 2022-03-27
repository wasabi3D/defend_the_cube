from GameManager.util import GameObject
import GameManager.singleton as sing

from GameExtensions.util import get_grid_pos, get_chunk_pos, PathFinder2NextChunk, PathFinderNoObstacles
from GameExtensions.util import grid_pos2world_pos
from GameExtensions.locals import N, W, S, E, CHUNK_SIZE

import pygame
from pygame.math import Vector2

from typing import Optional


class TestEnemy(GameObject):
    def __init__(self, pos: Vector2, image: pygame.Surface, name: str):
        super().__init__(pos, 0, image, name)
        self.objectives: list[Vector2] = [self.get_real_pos()]
        self.last_chunk: Optional[Vector2] = None
        self.chunk_path = PathFinderNoObstacles(get_chunk_pos(self.get_real_pos()),
                                                get_chunk_pos(sing.ROOT.game_objects["player"].get_real_pos()))

    def update(self) -> None:
        if len(self.objectives) == 0:
            return

        if get_chunk_pos(self.get_real_pos()) != self.last_chunk:
            print("hello")
            self.last_chunk = get_chunk_pos(self.get_real_pos())
            nxt_chunk = self.chunk_path.get_next()
            self.chunk_path.current = nxt_chunk
            chunk_diff = nxt_chunk - self.last_chunk
            if chunk_diff == Vector2(0, -1):
                d = N
            elif chunk_diff == Vector2(0, 1):
                d = S
            elif chunk_diff == Vector2(1, 0):
                d = E
            else:
                d = W
            chunk_topleft = self.last_chunk * CHUNK_SIZE
            pf = PathFinder2NextChunk(get_grid_pos(self.get_real_pos()), d, chunk_topleft - Vector2(-1, -1),
                                      chunk_topleft + Vector2(CHUNK_SIZE, CHUNK_SIZE) + Vector2(1, 1))
            path = pf.calculate()
            for p in path:
                self.objectives.append(grid_pos2world_pos(p))

        mov_vec = (self.objectives[0] - self.get_real_pos())
        dx = mov_vec.x
        dy = mov_vec.y

        rp = self.get_real_pos()
        dx_tmp_rect = self.image.get_rect(center=rp + Vector2(dx, 0))
        dy_tmp_rect = self.image.get_rect(center=rp + Vector2(0, dy))
        if sing.ROOT.is_colliding(dx_tmp_rect, exclude="enemy") != -1:
            dx = 0
        if sing.ROOT.is_colliding(dy_tmp_rect, exclude="enemy") != -1:
            dy = 0

        self.translate(Vector2(dx, dy))
        diff_x = abs(self.get_real_pos().x - self.objectives[0].x)
        diff_y = abs(self.get_real_pos().y - self.objectives[0].y)
        if diff_x < 5 and diff_y < 5:
            self.objectives.pop(0)
