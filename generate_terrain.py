import os
import random

import opensimplex as op
import pygame

pygame.init()

GRID_SIZE = (100, 100)
SIZE_BLOCK = 5
SCREEN_SIZE = (GRID_SIZE[0] * SIZE_BLOCK, GRID_SIZE[1] * SIZE_BLOCK)

FOREST_SIZE_SCALE = 0.08
FOREST_DENSITY_SCALE = 2

BEACH_WIDTH = 3

SCALE = 0.07


class Terrain:
    terrain = []
    mineral_layer = []
    over_terrain = []
    water_limit = -0.5
    sand_limit = -0.3
    tree_lim = 0.3
    tree_dens_lim = 0.3

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
                tmp = per.noise2(x * SCALE, y * SCALE)
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
                    for i in range(x - BEACH_WIDTH, x + BEACH_WIDTH + 1):
                        for j in range(y - BEACH_WIDTH, y + BEACH_WIDTH + 1):
                            if 0 <= i < size[0] and 0 <= j < size[1]:
                                if self.terrain[j][i] == self.GRASS and \
                                        self.get_distance_squared((x, y), (i, j)) \
                                        <= random.uniform(0, BEACH_WIDTH) ** 2:
                                    self.terrain[j][i] = self.SAND
        # on enlève le sable qui n'est ni à côté de l'eau ou de plus de sable
        # on en profite pour générer des arbres sur une liste différente au terrain (mais en s'y ajustant)
        tree_zones_noise = op.OpenSimplex(self.seed + 100)
        for y, line in enumerate(self.terrain):
            for x, el in enumerate(line):
                # lissage des plages
                if el == self.SAND:
                    tmp_change = True
                    for i in range(0, 3, 2):
                        tmp_x, tmp_y = x + i - 1, y + i - 1
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
                            x * FOREST_SIZE_SCALE, y * FOREST_SIZE_SCALE
                    ) > self.tree_lim and tree_zones_noise.noise2(
                        x * FOREST_DENSITY_SCALE, y * FOREST_DENSITY_SCALE
                    ) > self.tree_dens_lim:
                        self.over_terrain[y][x] = self.TREE

    def generate_mineral_patern(self, m_type, size_scale):
        pass

    def __init__(self, seed: int, size: tuple[int, int]) -> None:
        """
        :param seed: graine du onde
        :param size: taille de la carte
        """
        self.seed = seed
        random.seed(seed)
        self.per = op.OpenSimplex(seed)

        d = os.getcwd() + r"\resources\test\grid"
        print(d)
        self.GRASS = pygame.transform.scale(pygame.image.load(d + r"\grid_two.png"), (SIZE_BLOCK, SIZE_BLOCK))
        self.SAND = pygame.transform.scale(pygame.image.load(d + r"\grid_one.png"), (SIZE_BLOCK, SIZE_BLOCK))
        self.WATER = pygame.transform.scale(pygame.image.load(d + r"\grid_three.png"), (SIZE_BLOCK, SIZE_BLOCK))
        self.TREE = pygame.transform.scale(pygame.image.load(d + r"\tree.png"), (SIZE_BLOCK, SIZE_BLOCK))

        self.create_terrain(self.per, size)


if __name__ == "__main__":
    screen = pygame.display.set_mode(SCREEN_SIZE)
    ter = Terrain(200, GRID_SIZE)
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
