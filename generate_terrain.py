import os
import random

import opensimplex as op
import pygame

pygame.init()

GRID_SIZE = (300, 250)
SIZE_BLOCK = 4
SCREEN_SIZE = (GRID_SIZE[0] * SIZE_BLOCK, GRID_SIZE[1] * SIZE_BLOCK)


class Terrain:
    terrain = []
    mineral_layer = []
    over_terrain = []

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

    def generate_mineral_patern(self, m_type, size_scale):
        pass

    def __init__(self, seed: int,
                 size: tuple[int, int],
                 scale: float = 0.03,
                 forest_size_scale: float = 0.08,
                 forest_desity_scale: float = 2.,
                 beach_width: int = 3,
                 water_limit: float = -0.5,
                 tree_lim: float = 0.3,
                 tree_dens_lim: float = 0.3,
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
        random.seed(seed)
        self.per = op.OpenSimplex(seed)

        self.scale = scale

        # Variables en relation avec la forêt
        self.forest_size_scale = forest_size_scale
        self.forest_density_scale = forest_desity_scale

        self.beach_width = beach_width

        self.water_limit = water_limit
        self.tree_lim = tree_lim
        self.tree_dens_lim = tree_dens_lim

        d = os.getcwd() + r"\resources\test\grid"
        print(d)
        self.GRASS = pygame.transform.scale(pygame.image.load(d + r"\grid_two.png"), (SIZE_BLOCK, SIZE_BLOCK))
        self.SAND = pygame.transform.scale(pygame.image.load(d + r"\grid_one.png"), (SIZE_BLOCK, SIZE_BLOCK))
        self.WATER = pygame.transform.scale(pygame.image.load(d + r"\grid_three.png"), (SIZE_BLOCK, SIZE_BLOCK))
        self.TREE = pygame.transform.scale(pygame.image.load(d + r"\tree.png"), (SIZE_BLOCK, SIZE_BLOCK))

        self.create_terrain(self.per, size)


# Test de la génération
if __name__ == "__main__":
    screen = pygame.display.set_mode(SCREEN_SIZE)
    ter = Terrain(202, GRID_SIZE)
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

        pygame.display.update()
