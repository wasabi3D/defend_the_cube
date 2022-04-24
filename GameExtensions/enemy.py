import math

from GameManager.util import GameObject
import GameManager.singleton as sing

from GameExtensions.util import get_grid_pos, get_chunk_pos, MovementGenerator
from GameExtensions.util import grid_pos2world_pos, get_path2target, get_next_chunk, get_path2nxt_chunk
from GameExtensions.locals import N, W, S, E, CHUNK_SIZE, DIRS
from GameExtensions.resources import load_img

import pygame
from pygame.math import Vector2

from typing import Optional

import time


class Enemy(GameObject):  # Every enemy related class must inherit this
    def __init__(self, pos: Vector2, rotation: float, image: pygame.Surface, name: str):
        super().__init__(pos, rotation, image, name)
        self.hp = 100  # TMP


class TestEnemy(Enemy):
    def __init__(self, pos: Vector2, image: pygame.Surface, name: str):
        super().__init__(pos, 0, image, name)
        self.objectives: list[Vector2] = [self.get_real_pos()]
        self.cur_chunk: Optional[Vector2] = None

        self.objective_chunk = get_next_chunk(get_chunk_pos(self.get_real_pos()),
                                              get_chunk_pos(sing.ROOT.game_objects["player"].get_real_pos()))
        self.check_pos = self.get_real_pos().copy()
        self.last_checked = time.time()
        self.map = sing.ROOT.game_objects["terrain"].over_terrain
        self.movement_gen = MovementGenerator(self.image, self)
        sing.ROOT.add_collidable_object(self)

    def update(self) -> None:
        if self.hp < 0:
            sing.ROOT.remove_object(self)
            return
        player_pos = sing.ROOT.game_objects["player"].get_real_pos()
        dist = (self.get_real_pos().x - player_pos.x) ** 2 + (self.get_real_pos().y - player_pos.y) ** 2

        if get_chunk_pos(self.get_real_pos()) != self.cur_chunk or (len(self.objectives) == 0 and dist > 50):
            self.calculate_path(player_pos)
        if time.time() - self.last_checked > 5:
            if (self.get_real_pos() - self.check_pos).magnitude_squared() < 1:
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

        mov_vec = (self.objectives[0] - self.get_real_pos())
        if mov_vec.length_squared() > 0:
            mov_vec.normalize_ip()
        dx = mov_vec.x
        dy = mov_vec.y

        mov = self.movement_gen.move(dx, dy)

        if mov.x > 0 and abs(mov.x) > abs(mov.y):
            self.rotate(0, False)
        elif mov.x < 0 and abs(mov.x) > abs(mov.y):
            self.rotate(-math.pi, False)
        elif mov.y > 0:
            self.rotate(3 * math.pi / 2, False)
        elif mov.y < 0:
            self.rotate(math.pi / 2, False)

        self.translate(mov)
        diff_x = abs(self.get_real_pos().x - self.objectives[0].x)
        diff_y = abs(self.get_real_pos().y - self.objectives[0].y)
        if diff_x < 5 and diff_y < 5:
            self.objectives.pop(0)

    def calculate_path(self, player_pos):
        self.cur_chunk = get_chunk_pos(self.get_real_pos())
        self.objective_chunk = get_next_chunk(self.cur_chunk, get_chunk_pos(player_pos))
        chunk_diff = self.objective_chunk - self.cur_chunk
        if chunk_diff == Vector2(0, -1):
            d = N
        elif chunk_diff == Vector2(0, 1):
            d = S
        elif chunk_diff == Vector2(1, 0):
            d = E
        elif chunk_diff == Vector2(-1, 0):
            d = W
        else:
            tg = get_grid_pos(player_pos)
            pf = get_path2target(get_grid_pos(self.get_real_pos()), tg.x, tg.y)
            self.objectives += list(map(lambda pos: grid_pos2world_pos(pos), pf))
            return
        chunk_topleft = self.cur_chunk * CHUNK_SIZE
        pf = get_path2nxt_chunk(get_grid_pos(self.get_real_pos()), d,
                                pygame.Rect(chunk_topleft.x - 2, chunk_topleft.y - 2, CHUNK_SIZE + 2, CHUNK_SIZE + 2))
        self.objectives += list(map(lambda pos: grid_pos2world_pos(pos), pf))


class Zombie(TestEnemy):
    ATK = 10
    ATK_COOLDOWN = 2
    ATK_RANGE = 50
    KNOCKBACK_FORCE = 500

    def __init__(self, pos: Vector2, name: str):
        super().__init__(pos, load_img("resources/enemy/test_zombie.png"), name)
        self.timer = 0
        self.player = sing.ROOT.game_objects["player"]

    def update(self) -> None:
        super().update()
        dist = self.player.get_real_pos().distance_squared_to(self.get_real_pos())
        if dist <= Zombie.ATK_RANGE ** 2 and self.timer >= Zombie.ATK_COOLDOWN:
            self.player.hp -= self.ATK
            self.timer = 0
            self.player.knockback += (self.player.get_real_pos() - self.get_real_pos()).normalize() * \
                                    Zombie.KNOCKBACK_FORCE
        self.timer += sing.ROOT.delta
