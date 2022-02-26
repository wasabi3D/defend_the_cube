import os
import random

import opensimplex as op
import pygame

pygame.init()

GRID_SIZE = (600, 400)
SIZE_BLOCK = 2
SCREEN_SIZE = (GRID_SIZE[0] * SIZE_BLOCK, GRID_SIZE[1] * SIZE_BLOCK)


class Terrain:
    terrain = []
    mineral_layer = []
    over_terrain = []

    def __init__(self, seed: int,
                 size: tuple[int, int],
                 scale: float = 0.03,
                 forest_size_scale: float = 0.08,
                 forest_desity_scale: float = 2.,
                 beach_width: int = 3,
                 water_limit: float = -0.5,
                 tree_lim: float = 0.3,
                 tree_dens_lim: float = 0.3,
                 biome_chunk_size: int = 20
                 ) -> None:
        """
        :param seed: seed: graine du monde
        :param size: size: taille de la carte
        :param scale: scale: Échelle de bruit Simplex pour la génération de l'eau et l'herbe
        :param forest_size_scale: forest_size_scale: Échelle de bruit Simplex pour les zones de forêt
        :param forest_desity_scale: forest_desity_scale: Échelle de bruit Simplex pour la densité des forêts
        :param beach_width: Modifie jusquà quelle distance vont les plages
        :param water_limit: Modifie la taille dea plages mais pas la fréquance
        :param tree_lim: modifie la taille des forêts sans leur fréquance
        :param tree_dens_lim: Modifie la taille des groupes d'arbres
               dans les forêts (si forest density scale est assez basse)
        """

        self.seed = seed

        self.per = op.OpenSimplex(seed)

        self.scale = scale

        # Variables en relation avec la forêt
        self.forest_size_scale = forest_size_scale
        self.forest_density_scale = forest_desity_scale

        self.beach_width = beach_width

        self.water_limit = water_limit
        self.tree_lim = tree_lim
        self.tree_dens_lim = tree_dens_lim

        self.biome_chunk_size = biome_chunk_size

        d = os.getcwd() + r"\resources\test\grid"
        self.GRASS = pygame.transform.scale(pygame.image.load(d + r"\grid_two.png"), (SIZE_BLOCK, SIZE_BLOCK))
        self.SAND = pygame.transform.scale(pygame.image.load(d + r"\grid_one.png"), (SIZE_BLOCK, SIZE_BLOCK))
        self.WATER = pygame.transform.scale(pygame.image.load(d + r"\grid_three.png"), (SIZE_BLOCK, SIZE_BLOCK))
        self.TREE = pygame.transform.scale(pygame.image.load(d + r"\tree.png"), (SIZE_BLOCK, SIZE_BLOCK))

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
                    self.terrain[y].append(self.GRASS)
                self.over_terrain[y].append(None)

        # ici on rajouter les blocks de sable à la place des blocks d'herbe
        for y, line in enumerate(self.terrain):
            for x, el in enumerate(line):
                # on remplace l'herbe dans un carré
                if el == self.WATER:
                    for x2 in range(x - self.beach_width, x + self.beach_width + 1):
                        for y2 in range(y - self.beach_width, y + self.beach_width + 1):
                            if 0 <= x2 < size[0] and 0 <= y2 < size[1]:
                                random.seed(x2 + y2)
                                if self.terrain[y2][x2] == self.GRASS and \
                                        self.get_distance_squared((x, y), (x2, y2)) \
                                        <= random.uniform(0, self.beach_width) ** 2:
                                    self.terrain[y2][x2] = self.SAND
        # on enlève le sable qui n'est ni à côté de l'eau ou de plus de sable
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
                        self.terrain[y][x] = self.GRASS
                # arbres
                if self.terrain[y][x] == self.GRASS:
                    if tree_zones_noise.noise2(
                            x * self.forest_size_scale, y * self.forest_size_scale
                    ) > self.tree_lim and tree_zones_noise.noise2(
                        x * self.forest_density_scale, y * self.forest_density_scale
                    ) > self.tree_dens_lim:
                        self.over_terrain[y][x] = self.TREE


class Voronoi:
    points = {}

    def __init__(self, seed: int, chunk_size: int, chunk_types: list, minkowski_exponent: float = 2):
        assert chunk_size > 0, "Les tronçons doivent éxister! (leur taille doit être superieure à 0)"
        assert len(chunk_types) > 0, "Il doit y avoir au mois un type de biome!"

        self.seed = seed

        self.chunk_size = chunk_size
        self.chunk_types = chunk_types
        n_biomes = len(chunk_types)
        self.chunk_type_limits = [2 * (a + 1) / n_biomes - 1 for a in range(n_biomes - 1)]

        self.minkowski_exponent = minkowski_exponent

        self.rand_pos_x = op.OpenSimplex(seed)
        self.rand_pos_y = op.OpenSimplex(seed + 10)

    def noise2(self, x, y):
        def minkowski_distance_exp(x2: int, y2: int):
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
                if c_pos not in self.points:
                    random.seed(c_pos[1] * c_pos[0] + self.seed + 20)
                    self.points[c_pos] = (
                        random.randint(0, self.chunk_size - 1),
                        random.randint(0, self.chunk_size - 1)
                    )
                points[-1].append(self.points[c_pos])

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

        random.seed(sum(closest_point_chunk) + self.seed)
        return random.choice(self.chunk_types)


_d = os.getcwd() + r"\resources\test\grid"
_GRASS = pygame.transform.scale(pygame.image.load(_d + r"\grid_two.png"), (SIZE_BLOCK, SIZE_BLOCK))
_SAND = pygame.transform.scale(pygame.image.load(_d + r"\grid_one.png"), (SIZE_BLOCK, SIZE_BLOCK))
_WATER = pygame.transform.scale(pygame.image.load(_d + r"\grid_three.png"), (SIZE_BLOCK, SIZE_BLOCK))
_LAVA = pygame.transform.scale(pygame.image.load(_d + r"\grid_four.png"), (SIZE_BLOCK, SIZE_BLOCK))

# Test de la génération
if __name__ == "__main__":
    screen = pygame.display.set_mode(SCREEN_SIZE)

    ter = Terrain(202, GRID_SIZE)
    v = Voronoi(3, 20, [_GRASS, _SAND, _WATER, _LAVA], minkowski_exponent=4)
    # tab = [[v.noise2(j, i) for j in range(GRID_SIZE[0])]for i in range(GRID_SIZE[1])]
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        screen.fill((0, 0, 0))

        for i, t in enumerate(ter.terrain):
            for j, c in enumerate(t):
                screen.blit(c, c.get_rect(topleft=(j * SIZE_BLOCK, i * SIZE_BLOCK)))
                if ter.over_terrain[i][j] == ter.TREE:
                    screen.blit(
                        ter.over_terrain[i][j],
                        ter.over_terrain[i][j].get_rect(topleft=(j * SIZE_BLOCK, i * SIZE_BLOCK))
                    )
        # for i, t in enumerate(tab):
        #     for j, c in enumerate(t):
        #         screen.blit(c, c.get_rect(topleft=(j * SIZE_BLOCK, i * SIZE_BLOCK)))

        pygame.display.update()
