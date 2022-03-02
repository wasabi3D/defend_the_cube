import os
import random

import opensimplex as op
import pygame

from GameManager.util import GameObject
import GameManager.singleton as sing

pygame.init()

GRID_SIZE = (400, 400)
SIZE_BLOCK = 2
SCREEN_SIZE = (GRID_SIZE[0] * SIZE_BLOCK, GRID_SIZE[1] * SIZE_BLOCK)


class Terrain(GameObject):
    terrain = []
    mineral_layer = []
    over_terrain = []

    def __init__(self, seed: int,
                 size: tuple[int, int],
                 biome_types: list[pygame.Surface],
                 block_pixel_size: int,
                 scale: float = 0.03,
                 forest_size_scale: float = 0.08,
                 forest_density_scale: float = 2.,
                 beach_width: int = 3,
                 water_limit: float = -0.5,
                 tree_lim: float = 0.3,
                 tree_dens_lim: float = 0.3,
                 biome_chunk_size: int = 20,
                 minkowski_exponent: float = 2.
                 ) -> None:
        """
        :param seed: seed: graine du monde
        :param size: size: taille de la carte
        :param biome_types: types de biomes (image du carré)
        :param block_pixel_size: La dimension d'un block en pixels.
        :param scale: scale: Échelle de bruit Simplex pour la génération de l'eau et l'herbe
        :param forest_size_scale: forest_size_scale: Échelle de bruit Simplex pour les zones de forêt
        :param forest_density_scale: forest_desity_scale: Échelle de bruit Simplex pour la densité des forêts
        :param beach_width: Modifie jusquà quelle distance vont les plages
        :param water_limit: Modifie la taille dea plages mais pas la fréquance
        :param tree_lim: modifie la taille des forêts sans leur fréquance
        :param tree_dens_lim: Modifie la taille des groupes d'arbres
               dans les forêts (si forest density scale est assez basse)
        :param biome_chunk_size: Taille des tronçons (modifie la taille des biomes
        :param minkowski_exponent: exponentiel pour calculer les distances de Minkowski pour le bruit de Veronoi
        """
        super().__init__(pygame.Vector2(0, 0), 0, pygame.Surface((0, 0)), "terrain")

        self.seed = seed

        self.per = op.OpenSimplex(seed)

        self.block_px_size = block_pixel_size

        self.size = size

        self.scale = scale

        # Variables en relation avec la forêt
        self.forest_size_scale = forest_size_scale
        self.forest_density_scale = forest_density_scale

        self.beach_width = beach_width

        self.water_limit = water_limit
        self.tree_lim = tree_lim
        self.tree_dens_lim = tree_dens_lim

        d = os.getcwd() + r"\resources\test\grid"
        self.GRASS = pygame.transform.scale(pygame.image.load(d + r"\grid_two.png"),
                                            (block_pixel_size, block_pixel_size))
        self.SAND = pygame.transform.scale(pygame.image.load(d + r"\grid_one.png"),
                                           (block_pixel_size, block_pixel_size))
        self.WATER = pygame.transform.scale(pygame.image.load(d + r"\grid_three.png"),
                                            (block_pixel_size, block_pixel_size))
        self.TREE = pygame.transform.scale(pygame.image.load(d + r"\tree.png"),
                                           (block_pixel_size, block_pixel_size))

        self.biome_types = biome_types
        self.voronoi = Voronoi(seed=seed + 11, chunk_size=biome_chunk_size,
                               chunk_types=biome_types, minkowski_exponent=minkowski_exponent)

        self.create_terrain(self.per, size)

    @staticmethod
    def get_distance_squared(pos1: tuple[int, int], pos2: tuple[int, int]) -> int:
        return (pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2

    def create_terrain(self, per: op.OpenSimplex, size: tuple[int, int]) -> None:
        """ Cree grace au bruit de Perlin (Prelin's noise), sa deuxième version donc le Simplex,
        une carte avec de l'herbe, du sable et de l'eau et des arbres
        :param per: L'objet nous permettant d'avoir les valeurs de chaque case (module opensimplex)
        :param size: taille de la carte (en blocks) en (x, y)
        """

        for y in range(size[1]):
            self.terrain.append([])
            self.over_terrain.append([])
            for x in range(size[0]):
                # ici on utilise les plages de valeurs pour définir ce qu'il y a sur chaque case (basé sur le Simplex)
                tmp = per.noise2(x * self.scale, y * self.scale)
                if tmp < self.water_limit:
                    self.terrain[y].append(self.WATER)
                else:
                    self.terrain[y].append(self.voronoi.noise2(x, y))
                self.over_terrain[y].append(None)

        # ici on rajouter les blocks de sable à la place des blocks d'herbe
        for y, line in enumerate(self.terrain):
            for x, el in enumerate(line):
                # on remplace l'herbe dans un carré
                if el == self.WATER:
                    for x2 in range(x - self.beach_width, x + self.beach_width + 1):
                        for y2 in range(y - self.beach_width, y + self.beach_width + 1):
                            if 0 <= x2 < size[0] and 0 <= y2 < size[1]:
                                random.seed(x2 * y2)
                                # on enlève le sable qui n'est ni à côté de l'eau ou de plus de sable
                                if self.terrain[y2][x2] in self.biome_types and \
                                        self.get_distance_squared((x, y), (x2, y2)) \
                                        <= random.uniform(0, self.beach_width) ** 2:
                                    self.terrain[y2][x2] = self.SAND
        # on en profite pour générer des arbres sur une liste différente au terrain (mais en s'y ajustant)
        tree_zones_noise = op.OpenSimplex(self.seed + 100)
        for y, line in enumerate(self.terrain):
            for x, el in enumerate(line):
                # lissage des plages
                if el == self.SAND:
                    tmp_change = True
                    for p in range(0, 3, 2):
                        tmp_x, tmp_y = x + p - 1, y + p - 1
                        if 0 <= tmp_x < size[0] and 0 <= tmp_y < size[1]:
                            tmp_elx, tmp_ely = self.terrain[y][tmp_x], self.terrain[tmp_y][x]
                            if (tmp_elx == self.SAND or tmp_elx == self.WATER or
                                    tmp_elx == self.SAND or tmp_elx == self.WATER):
                                tmp_change = False
                                break
                    if tmp_change:
                        self.terrain[y][x] = self.voronoi.noise2(x, y)
                # arbres
                if self.terrain[y][x] in self.biome_types:
                    if tree_zones_noise.noise2(
                            x * self.forest_size_scale, y * self.forest_size_scale
                    ) > self.tree_lim and tree_zones_noise.noise2(
                        x * self.forest_density_scale, y * self.forest_density_scale
                    ) > self.tree_dens_lim:
                        self.over_terrain[y][x] = self.TREE

    def blit(self, scr: pygame.Surface) -> None:
        center_x = self.get_real_pos().x
        center_y = self.get_real_pos().y
        x_dim_half, y_dim_half = self.size[0] * self.block_px_size / 2, self.size[1] * self.block_px_size / 2
        scr_width_half, scr_height_half = sing.ROOT.screen_dim[0] / 2, sing.ROOT.screen_dim[1] / 2

        top_coord = center_y - y_dim_half
        top_diff = sing.ROOT.camera_pos.y - scr_height_half - top_coord
        top_start_index = int(top_diff // self.block_px_size - 1)
        bottom_index = min(self.size[1] - 1, top_start_index + sing.ROOT.screen_dim[1] // self.block_px_size + 7)
        top_start_index = max(0, top_start_index)

        left_coord = center_x - x_dim_half
        left_diff = sing.ROOT.camera_pos.x - scr_width_half - left_coord
        left_start_index = int(left_diff // self.block_px_size - 1)
        right_index = min(self.size[0] - 1, left_start_index + sing.ROOT.screen_dim[0] // self.block_px_size + 7)
        left_start_index = max(0, left_start_index)

        # print("aa", top_diff)
        # print("VERTICAL", top_start_index, bottom_index)
        # print("HORIZONTAL", left_start_index, right_index)
        for i, t in enumerate(self.terrain[top_start_index:bottom_index]):
            new_i = i + top_start_index
            y = new_i * self.block_px_size + center_y - y_dim_half - sing.ROOT.camera_pos.y + scr_height_half
            for j, c in enumerate(t[left_start_index:right_index]):
                new_j = j + left_start_index
                x = new_j * self.block_px_size + center_x - x_dim_half - sing.ROOT.camera_pos.x + scr_width_half
                scr.blit(c, c.get_rect(topleft=(x, y)))
                if self.over_terrain[new_i][new_j] is not None:
                    scr.blit(
                        self.over_terrain[new_i][new_j],
                        self.over_terrain[new_i][new_j].get_rect(topleft=(x, y))
                    )


# Classe permettant de générer un bruit de Voronoi qu'on utilise pour délimiter des zones
class Voronoi:
    points = {}  # cette variable permet de rendre la génération de terrain plus rapide

    def __init__(self, seed: int, chunk_size: int, chunk_types: list, minkowski_exponent: float = 2):
        """
        :param seed: graine de la génération
        :param chunk_size: taille des tronçons (répartition des points
        :param chunk_types: différants types de points (zones ou biomes)
        :param minkowski_exponent: l'exponentiel pour le calcul des distances (2 == théorème de Pythagore)
        """
        assert chunk_size > 0, "Les tronçons doivent éxister! (leur taille doit être superieure à 0)"
        assert len(chunk_types) > 0, "Il doit y avoir au mois un type de biome!"

        self.seed = seed

        self.chunk_size = chunk_size
        self.chunk_types = chunk_types

        self.minkowski_exponent = minkowski_exponent

    def noise2(self, x, y):
        """ Cette fonction nous permet d'avoir le type du point de coordonnées données
        qui est choisi au hazar dans les types de tronçons
        :param x: position x du point
        :param y: position y du point
        :return: type du point (donné dans la création de l'objet)
        """

        def minkowski_distance_exp(x2: int, y2: int):
            """ Calcule la distance avec la formule de Minkowski à la puissance
            :param x2: position x du point
            :param y2: position y du point
            :return: la distance de Minkowski entre le point donné et le point de coordonées (x, y)
            """
            return abs(x - x2) ** self.minkowski_exponent + abs(y - y2) ** self.minkowski_exponent

        # On repère les coordonées du tronçon dans lequel le point se situe
        chunk_x = x // self.chunk_size
        chunk_y = y // self.chunk_size

        # ici on définit les coordonées du point de chaque tronçon dans le tronçon ((0;0) étant en haut à gauche)
        points = []
        for j in range(chunk_y - 2, chunk_y + 3):
            points.append([])
            for i in range(chunk_x - 2, chunk_x + 3):
                c_pos = (i, j)
                # On utilise un diccionnaire pour accélérer la génération
                if c_pos not in self.points:
                    # les seed servent à avoir toujours la même chose même si on les répète plusieurs fois
                    random.seed(c_pos[1] * (c_pos[0] + 1) + self.seed + 20)
                    self.points[c_pos] = (
                        random.randint(0, self.chunk_size - 1),
                        random.randint(0, self.chunk_size - 1)
                    )
                points[-1].append(self.points[c_pos])

        # à partir d'ici on cherche le tronçaon dont le point est le plus proche
        closest_point_chunk = (chunk_x - 2, chunk_y - 2)
        dist = minkowski_distance_exp(self.chunk_size * (chunk_x - 2) + points[0][0][0],
                                      self.chunk_size * (chunk_y - 2) + points[0][0][1])
        for i_y, line in enumerate(points):
            for i_x, point in enumerate(line):
                true_ix = self.chunk_size * (chunk_x + i_x - 1) + point[0]
                true_iy = self.chunk_size * (chunk_y + i_y - 1) + point[1]
                tmp_dist = minkowski_distance_exp(true_ix, true_iy)
                if tmp_dist < dist:
                    closest_point_chunk = (true_ix, true_iy)
                    dist = tmp_dist

        # finalement on utilise les seed pour que tous les points dans la zone du tronçon soient du même type
        random.seed(closest_point_chunk[0] * (closest_point_chunk[1] + 1) + self.seed)
        return random.choice(self.chunk_types)


# Test de la génération
if __name__ == "__main__":
    _d = os.getcwd() + r"\resources\test\grid"
    _GRASS = pygame.transform.scale(pygame.image.load(_d + r"\grid_two.png"), (SIZE_BLOCK, SIZE_BLOCK))
    _SAND = pygame.transform.scale(pygame.image.load(_d + r"\grid_one.png"), (SIZE_BLOCK, SIZE_BLOCK))
    _WATER = pygame.transform.scale(pygame.image.load(_d + r"\grid_three.png"), (SIZE_BLOCK, SIZE_BLOCK))
    _LAVA = pygame.transform.scale(pygame.image.load(_d + r"\grid_four.png"), (SIZE_BLOCK, SIZE_BLOCK))
    _DARK_GRASS = pygame.transform.scale(pygame.image.load(_d + r"\dark_grass.png"), (SIZE_BLOCK, SIZE_BLOCK))

    ter = Terrain(23452345,
                  size=GRID_SIZE,
                  minkowski_exponent=25,
                  biome_types=[_GRASS, _DARK_GRASS],
                  biome_chunk_size=30
                  )

    screen = pygame.display.set_mode(SCREEN_SIZE)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        screen.fill((0, 0, 0))

        for i, t in enumerate(ter.terrain):
            for j, c in enumerate(t):
                screen.blit(c, c.get_rect(topleft=(j * SIZE_BLOCK, i * SIZE_BLOCK)))
                if ter.over_terrain[i][j] is not None:
                    screen.blit(
                        ter.over_terrain[i][j],
                        ter.over_terrain[i][j].get_rect(topleft=(j * SIZE_BLOCK, i * SIZE_BLOCK))
                    )

        pygame.display.update()
