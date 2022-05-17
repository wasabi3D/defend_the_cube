import math

import GameManager.singleton as sing

from GameExtensions.util import get_grid_pos, get_chunk_pos, Entity
from GameExtensions.util import grid_pos2world_pos, get_path2target, get_next_chunk, get_path2nxt_chunk
from GameExtensions.locals import N, W, S, E, CHUNK_SIZE, DIRS, ENEMY
from GameExtensions.resources import load_img
from GameExtensions.field_objects import Placeable

import pygame
from pygame.math import Vector2

from typing import Optional

import time


class Enemy(Entity):  # Every enemy related class must inherit this
    """
    La base de tous les ennemis
    """
    def __init__(self, pos: Vector2, rotation: float, image: pygame.Surface, name: str, hp: int, max_hp: int):
        """

        :param pos: La position initiale de l'objet. La valeur par défaut est pygame.Vector2(0, 0).
        :param rotation: La rotation en radian initiale de l'objet. La valeur par défaut est 0.
        :param image: L'image de l'objet initiale.
        :param name: Le nom de l'objet.
        :param hp: La vie que l'ennemi possède
        :param max_hp: Max de vie que cet ennemi peut avoir
        """
        super().__init__(pos, rotation, image, name, hp, max_hp, image)
        self.tags.append(ENEMY)


class TestEnemy(Enemy):
    """
    Un modèle d'ennemi qui possède un système pour trouver un chemin vers le joueur
    L'algorithme utilisé ici est A*
    """
    def __init__(self, pos: Vector2, image: pygame.Surface, name: str, hp: int, speed: int):
        """
        :param pos: La position initiale de l'objet. La valeur par défaut est pygame.Vector2(0, 0).
        :param rotation: La rotation en radian initiale de l'objet. La valeur par défaut est 0.
        :param image: L'image de l'objet initiale.
        :param name: Le nom de l'objet.
        :param hp: La vie que l'ennemi possède
        :param speed: La vitesse dont cet ennemi avance
        """
        super().__init__(pos, 0, image, name, hp, hp)
        self.objectives: list[Vector2] = [self.get_real_pos()]
        self.cur_chunk: Optional[Vector2] = None

        self.objective_chunk = get_next_chunk(get_chunk_pos(self.get_real_pos()),
                                              get_chunk_pos(sing.ROOT.game_objects["player"].get_real_pos()))
        self.check_pos = self.get_real_pos().copy()
        self.last_checked = time.time()
        self.map = sing.ROOT.game_objects["terrain"].over_terrain
        self.speed = speed
        sing.ROOT.add_collidable_object(self)

    def update(self) -> None:
        super().update()
        if self.hp <= 0:
            sing.ROOT.remove_object(self)
            return
        core_pos = sing.ROOT.game_objects["core"].get_real_pos()
        player_pos = sing.ROOT.game_objects["player"].get_real_pos()
        if core_pos.distance_squared_to(self.get_real_pos()) < player_pos.distance_squared_to(self.get_real_pos())\
                or sing.ROOT.game_objects["player"].ghost_mode:
            player_pos = core_pos.copy()
        dist = (self.get_real_pos().x - player_pos.x) ** 2 + (self.get_real_pos().y - player_pos.y) ** 2

        if get_chunk_pos(self.get_real_pos()) != self.cur_chunk or (len(self.objectives) == 0 and dist > 50):
            self.calculate_path(player_pos)
        if time.time() - self.last_checked > 1.5:
            if (self.get_real_pos() - self.check_pos).magnitude_squared() < 1:
                grid_pos = get_grid_pos(self.get_real_pos())
                for d in DIRS:
                    obj = self.map[int(grid_pos.y + d[0])][int(grid_pos.x + d[1])]
                    if obj is None:
                        continue
                    elif isinstance(obj, Placeable):
                        obj.damage(5)
                self.objectives.clear()
                self.calculate_path(player_pos)
            self.check_pos = self.get_real_pos().copy()
            self.last_checked = time.time()

        if len(self.objectives) == 0:
            return

        mov_vec = (self.objectives[0] - self.get_real_pos())
        if mov_vec.length_squared() > 0:
            mov_vec = mov_vec.normalize() * self.speed
        dx = mov_vec.x
        dy = mov_vec.y

        mov = self.mov_gen.move(dx, dy)

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
        """
        Calcule un chemin qui permet de trouver un chemin qui va vers le joueur en utilisant l'algorithme A*

        :param player_pos: La position du joueur

        """
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
    """
    Classe qui définit le zombie
    """
    ATK = 5
    ATK_COOLDOWN = 2
    ATK_RANGE = 50
    KNOCKBACK_FORCE = 550
    MAX_HP = 100

    def __init__(self, pos: Vector2, name: str):
        """

        :param pos: La position initiale
        :param name: Le nom de cet objet
        """
        super().__init__(pos, load_img("resources/enemy/test_zombie.png"), name, Zombie.MAX_HP, 0.5)
        self.timer = 0
        self.player = sing.ROOT.game_objects["player"]
        self.mov_gen.exclude = "Zombie.*"

    def update(self) -> None:
        super().update()
        dist = self.player.get_real_pos().distance_squared_to(self.get_real_pos())
        dist_core = sing.ROOT.game_objects["core"].get_real_pos().distance_squared_to(self.get_real_pos())
        if dist <= Zombie.ATK_RANGE ** 2 and self.timer >= Zombie.ATK_COOLDOWN and not self.player.ghost_mode:
            self.timer = 0
            self.player.get_damage(self.ATK, (self.player.get_real_pos() - self.get_real_pos()).normalize() * \
                                   Zombie.KNOCKBACK_FORCE)
        elif dist_core <= (Zombie.ATK_RANGE + 20) ** 2 and self.timer >= Zombie.ATK_COOLDOWN:
            self.timer = 0
            sing.ROOT.game_objects["core"].damage(self.ATK)
        self.timer += sing.ROOT.delta
