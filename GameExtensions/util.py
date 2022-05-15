import typing
from typing import Union, Optional

import math
from queue import PriorityQueue

import pygame
from pygame.math import Vector2

import GameManager.singleton as sing
from GameManager.resources import load_img
from GameManager.util import tuple2Vec2, GameObject, rad2deg

from GameExtensions.locals import N, S, W, E, CHUNK_SIZE, DIRS, WATER_DECEL


def get_grid_pos(coordinate: Vector2) -> Vector2:
    """
    Permet de calculer la position sur le grid en fonction de la position universelle.
    
    :param coordinate: La position universelle
    :return: La position sur le grid
    """
    from GameExtensions.generate_terrain import Terrain
    terrain: Terrain = sing.ROOT.game_objects["terrain"]
    if not isinstance(terrain, Terrain):
        raise TypeError("Not an instance of Terrain.")
    map_pos = terrain.get_real_pos()
    dim_per_block = terrain.block_px_size
    rel_pos = coordinate - map_pos + Vector2(terrain.block_px_size, terrain.block_px_size) / 2
    rel_pos = rel_pos // dim_per_block
    rel_pos += Vector2(len(terrain.over_terrain[0]) // 2, len(terrain.over_terrain) // 2)
    return rel_pos


def get_chunk_pos(coordinate: Vector2, chunk_size: int = CHUNK_SIZE) -> Vector2:
    """
    Calcule les coordonnées du chunk en fonction des coordonnées donnés

    :param coordinate: La position universelle
    :param chunk_size: La taille d'un chunk
    :return: Les coordonnées du chunk
    """
    return get_grid_pos(coordinate) // chunk_size


def grid_pos2world_pos(coordinate: Vector2) -> Vector2:
    """
    Convertit la position sur le grid en position universelle

    :param coordinate: La position sur le grid
    :return: La position convertie
    """
    from GameExtensions.generate_terrain import Terrain
    terrain: Terrain = sing.ROOT.game_objects["terrain"]
    if not isinstance(terrain, Terrain):
        raise TypeError("Not an instance of Terrain.")
    map_pos = terrain.get_real_pos()

    return coordinate * terrain.block_px_size + map_pos - tuple2Vec2(terrain.size) * terrain.block_px_size / 2


class ShakeGenerator:
    """
    Classe qui permet de générer un tremblement.
    """

    def __init__(self,
                 x_intensity: Union[int, float],
                 y_intensity: Union[int, float],
                 x_cycle: Union[int, float],
                 y_cycle: Union[int, float],
                 x_offset: Union[int, float],
                 y_offset: Union[int, float],
                 x_intensity_decay: Union[int, float],
                 y_intensity_decay: Union[int, float],
                 wave_func=math.sin):
        """
        :param x_intensity: Intensité du tremblement de l'abscisse
        :param y_intensity: Intensité du tremblement de l'ordonnée
        :param x_cycle: Modifie la période du tremblement de l'abscisse
        :param y_cycle: Modifie la période du tremblement de l'ordonnée
        :param x_offset: Décale la période de l'abscisse d'un certain temps
        :param y_offset: Décale la période de l'ordonnée d'un certain temps
        :param x_intensity_decay: Comment diminuer l'intensité du tremblement de l'abcisse à chaque frame
        :param y_intensity_decay: Comment diminuer l'intensité du tremblement de l'ordonnée à chaque frame
        :param wave_func: Fonction periodique utilisée pour générer le tremblement
        """
        self.x_intensity = x_intensity
        self.y_intensity = y_intensity
        self.x_cycle = x_cycle
        self.y_cycle = y_cycle
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.x_intensity_decay = x_intensity_decay
        self.y_intensity_decay = y_intensity_decay
        self.f = wave_func

        self.time = 0
        self.cur_x_int = 0
        self.cur_y_int = 0
        self.shaking = False
        self.shake_stop_threshold = 0.001

    def begin(self, time=0) -> None:
        """
        Commence et initialise la génération du tremblement
        :param time: Le point de départ
        """
        self.time = time
        self.cur_x_int = self.x_intensity
        self.cur_y_int = self.y_intensity
        self.shaking = True

    def next_frame(self, delta: Union[float, int]) -> None:
        """
        Fait avancer le tremblement d'un certain temps
        :param delta: Variation de temps entre 2 frame consécutifs
        """
        if self.shaking:
            self.cur_x_int *= self.x_intensity_decay
            self.cur_y_int *= self.y_intensity_decay
            self.time += delta

            if self.cur_x_int < self.shake_stop_threshold and self.cur_y_int < self.shake_stop_threshold:
                self.shaking = False

    def get_shake(self) -> pygame.Vector2:
        """
        Génére le tremblement à t=self.time
        :return: Un pygame.Vector2 qui représente le tremblement
        """
        if self.shaking:
            return pygame.Vector2(self.cur_x_int * self.f(self.time * self.x_cycle + self.x_offset),
                                  self.cur_y_int * self.f(self.time * self.y_cycle + self.y_offset))
        else:
            return pygame.Vector2(0, 0)


class Animation:
    def __init__(self, frames: list[pygame.Surface], frame_interval: float, goto_on_end: Optional[str] = None):
        self.frames = frames
        self.interval = frame_interval
        self.on_end = goto_on_end


class Animator:
    """
    Classe qui permet de controller une animation d'un objet.
    """

    def __init__(self):
        self.animations: dict[str, Animation] = {}
        self.current: typing.Optional[str] = None
        self.cur_frame = 0
        self.timer = 0

    def register_anim(self, name: str, anim: Animation) -> None:
        """
        Ajouter une nouvelle animation

        :param name: Le nom
        :param anim: L'animation
        """
        self.animations.setdefault(name, anim)

    def start_anim(self, name: str) -> None:
        """
        Commence une animation du début

        :param name: Le nom de l'animation qu'on veut commencer
        """
        self.current = name
        self.cur_frame = 0
        self.timer = 0

    def update(self, delta: float) -> None:
        """
        Fonction appellée pour faire avancer l'animation

        :param delta: Le temps écoulé pendant la dernière frame
        """
        if self.current is None:
            return
        self.timer += delta
        if self.animations[self.current].interval <= self.timer:
            self.cur_frame += 1
            if self.cur_frame > len(self.animations[self.current].frames) - 1 \
                    and self.animations[self.current].on_end is not None:
                self.current = self.animations[self.current].on_end
                self.cur_frame = 0

            self.cur_frame %= len(self.animations[self.current].frames)
            self.timer = 0

    def get_cur_frame(self, rotation: Optional[float] = None) -> pygame.Surface:
        """
        Renvoie la frame de l'animation actuelle.

        :return: La frame
        """
        img = self.animations[self.current].frames[self.cur_frame]
        if rotation is None:
            return img
        else:
            return pygame.transform.rotate(img, rad2deg(rotation))

    @staticmethod
    def load_frames_by_pattern(base_file_name: str, suffix: str, start_i: int, end_i: int, conv=lambda s: s,
                               override_size: typing.Optional[tuple[int, int]] = None) -> list[pygame.Surface]:
        """
        Permet de charger plusieurs images avec un pattern de nom.

        :param base_file_name: La base des noms dans tous les fichiers
        :param suffix: Le suffixe des fichiers (ex. xx.png)
        :param start_i: Début du pattern
        :param end_i: Fin du pattern
        :param conv: Fonction pour convertir les images éventuellement
        :param override_size: La taille des images
        :return: Une liste des images
        """
        lst = []
        for i in range(start_i, end_i + 1):
            lst.append(conv(load_img(f"{base_file_name}{i}{suffix}", override_size)))
        return lst


class Path:
    """
    Classe utilisée pour calculer un chemin avec l'algorithme A*. Represente un chemin
    """

    def __init__(self, coords: list[Vector2], cost=0):
        self.coords: list[Vector2] = coords
        self.cost = cost

    def copy(self):
        return Path(self.coords.copy(), self.cost)

    def __lt__(self, other):
        return self.cost < other.cost


def get_next_chunk(current_pos: Vector2,
                   target_pos: Vector2) -> Vector2:
    """
    Fonction qui permet de calculer vers quel chunk parmi les chunks adjacentes que
     l'ennemi doit aller pour aller jusqu'au joueur.

    :param current_pos: La position actuelle sur le grid
    :param target_pos: La position actuelle du goal sur le grid
    :return: Les coordonnées du prochain chunk
    """
    diff_x = current_pos.x - target_pos.x
    diff_y = current_pos.y - target_pos.y
    if current_pos == target_pos:
        return current_pos
    elif abs(diff_x) > abs(diff_y):
        return current_pos + Vector2(1 if diff_x < 0 else -1, 0)
    else:
        return current_pos + Vector2(0, 1 if diff_y < 0 else -1)


def get_path2target(current_pos: Vector2,
                    target_x: Optional[int],
                    target_y: Optional[int],
                    chunk_limit: Optional[pygame.Rect] = None,
                    iter_limit: int = 12) -> list[Vector2]:
    """
    Calcule  un chemin pour aller à la case souhaitée à l'aide de l'algorithme A* (A-Star)

    :param current_pos: La position actuelle sur le grid
    :param target_x: L'abcisse de la case de goal
    :param target_y: L'ordonnée de la case de goal
    :param chunk_limit: Le chunk dans lequel l'algorithme va être forcé à trouver un chemin dedans.
    :param iter_limit:
    :return: Une liste des cases que l'ennemi? doit suivre
    """
    queue: PriorityQueue[Path] = PriorityQueue()
    queue.put(Path([current_pos.copy()]))

    ter = sing.ROOT.game_objects["terrain"].over_terrain
    counter = 0

    while True:
        cur = queue.get()
        if counter > iter_limit:
            return cur.coords
        if (target_x is None or target_y is None) and (cur.coords[-1].x == target_x or cur.coords[-1].y == target_y):
            return cur.coords
        elif cur.coords[-1].x == target_x and cur.coords[-1].y == target_y:
            return cur.coords

        for d in DIRS:
            nxt = Vector2(cur.coords[-1].x + d[0], cur.coords[-1].y + d[1])
            if chunk_limit is not None:
                if (not chunk_limit.topleft[0] <= nxt.x <= chunk_limit.bottomright[0]) or \
                        (not chunk_limit.topleft[1] <= nxt.y <= chunk_limit.bottomright[1]) or \
                        ter[int(nxt.y)][int(nxt.x)] is not None or \
                        nxt in cur.coords:
                    continue

            new_path = cur.copy()
            new_path.coords.append(nxt)
            new_path.cost = (len(new_path.coords) + (((target_x - nxt.x) if target_x is not None else 0) ** 2 +
                                                     ((target_y - nxt.y) if target_y is not None else 0) ** 2))
            queue.put(new_path)
        counter += 1


def get_path2nxt_chunk(current_pos: Vector2,
                       target_dir: str,
                       chunk_limit: pygame.Rect) -> list[Vector2]:
    """
    Fonction qui permet de trouver un chemin pour aller au prochain chunk

    :param current_pos: La position actuell sur le grid
    :param target_dir: La direction à laquelle qu'on veut avancer
    :param chunk_limit: La taille d'un chunk
    :return: Une liste de position que l'enemi? doit suivre
    """
    x_obj, y_obj = None, None
    if target_dir == N:
        y_obj = chunk_limit.topleft[1]
    elif target_dir == S:
        y_obj = chunk_limit.bottomright[1]
    elif target_dir == E:
        x_obj = chunk_limit.bottomright[0]
    elif target_dir == W:
        x_obj = chunk_limit.topleft[0]
    return get_path2target(current_pos, x_obj, y_obj, chunk_limit)


class MovementGenerator:
    """
    Classe qui permet de générer un mouvement qui respecte les hiboxes
    """

    def __init__(self,
                 hitbox: pygame.Surface,
                 ref: GameObject,
                 knockback_decay: float = 0.1,
                 exclude: Optional[str] = None):
        """

        :param hitbox: Un pygame.Surface qui définit la taille du hitbox
        :param ref: le gameobject qui utilise cette instance
        :param exclude: Le nom des objets exclus lors de la détection des collisions
        """
        from GameExtensions.generate_terrain import Terrain
        self.hitbox = hitbox
        self.ref = ref
        self.terrain: Terrain = sing.ROOT.game_objects["terrain"]
        self.knockback = Vector2(0, 0)
        self.kb_decay = knockback_decay
        self.exclude = ref.name if exclude is None else exclude

    def update_knockback(self):
        self.knockback -= self.knockback * self.kb_decay

    def move(self, dx: Union[int, float], dy: Union[int, float], include_knockback=True) -> Vector2:
        """
        Retourne un mouvement valide en fonction de dx et dy

        :param dx: Variation de la position sur l'abcisse
        :param dy: Variation de la position sur l'ordonnée
        :param include_knockback: Si on prend en compte le knockback ou pas
        :return: Le vecteur mouvement final
        """
        # Check for collisions  https://youtu.be/m7GnJo_oZUU
        if include_knockback:
            dx += self.knockback.x * sing.ROOT.delta
            dy += self.knockback.y * sing.ROOT.delta
        rp = self.ref.get_real_pos()
        dx_tmp_rect = self.hitbox.get_rect(center=rp + Vector2(dx, 0))
        dy_tmp_rect = self.hitbox.get_rect(center=rp + Vector2(0, dy))
        if sing.ROOT.is_colliding(dx_tmp_rect, exclude=self.exclude) != -1:
            dx = 0
        if sing.ROOT.is_colliding(dy_tmp_rect, exclude=self.exclude) != -1:
            dy = 0

        vec = Vector2(dx, dy)

        grid_pos = get_grid_pos(rp)
        if self.terrain.terrain[int(grid_pos.y)][int(grid_pos.x)] == self.terrain.WATER:
            vec *= WATER_DECEL

        return vec


class Entity(GameObject):
    """
    Une clase qui généralise les entités comme les ennemis, le joueur.
    """
    def __init__(self, pos: Vector2,
                 rotation: float,
                 image: pygame.Surface,
                 name: str,
                 hp: int,
                 max_hp: int,
                 hitbox: Optional[pygame.Surface] = None):
        """

        :param pos: La position initiale
        :param rotation: La rotation
        :param image: L'image de l'entité
        :param name: Le nom de l'entité
        :param hp: La quantité de la vie que cette entité possède
        :param max_hp: Le maximum de la quantité de la vie
        :param hitbox: La hitbox de cette entité
        """
        super().__init__(pos, rotation, image, name)
        self.mov_gen = MovementGenerator(hitbox if hitbox is not None else self.image, self)
        self.hp = hp
        self.max_hp = max_hp

    def get_damage(self, amount: int, knockback_force: Optional[Vector2] = None) -> None:
        """
        Fonction pour donner du dégat

        :param amount: La quantité du dégat
        :param knockback_force: Un vecteur qui représente comment cette entité est repoussé
        """
        self.hp = max(min(self.hp - amount, self.max_hp), 0)
        if knockback_force is not None:
            self.mov_gen.knockback += knockback_force

    def update(self) -> None:
        super().update()
        self.mov_gen.update_knockback()


class HPBar(GameObject):
    """
    La classe pour la barre qui affiche l'HP
    """

    class RedFill(GameObject):
        """
        La partie rouge de la barre
        """
        def __init__(self, prop: float, size):
            """

            :param prop: Proportion de la taille par rapport à l'image originale
            """
            super().__init__(Vector2(0, 0), 0, load_img("resources/UI/hp_bar_fill.png", size), "red")
            self.prop = prop

        def blit(self, screen: pygame.Surface, apply_alpha=False) -> None:
            rect = self.image.get_rect(center=self.get_screen_pos())
            rect.update(rect.left, rect.top, rect.width * self.prop, rect.height)
            screen.blit(self.image, rect.topleft, (0, 0, rect.width, rect.height))

    def __init__(self, pos: Vector2, proportion=1, size=(480, 48)):
        """

        :param pos: La position sur l'écran
        :param proportion: Proportion de la taille de la barre rouge par rapport à l'image originale
        """
        super().__init__(pos, 0, load_img("resources/UI/hp_bar_frame.png", size), "HPBar")

        self.prop = proportion
        self.children.add_gameobject(HPBar.RedFill(self.prop, size))
        self.size = size

    def blit(self, screen: pygame.Surface, apply_alpha=False) -> None:
        self.children["red"].prop = self.prop
        super().blit(screen, apply_alpha)

