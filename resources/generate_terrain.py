import os
import random

import opensimplex as op
import pygame

pygame.init()

GRID_SIZE = (100, 100)
SIZE_BLOCK = 5
SCREEN_SIZE = (GRID_SIZE[0] * SIZE_BLOCK, GRID_SIZE[1] * SIZE_BLOCK)

BEACH_WIDTH = 3


class Terrain:
    terrain = []
    water_limit = -0.5
    sand_limit = -0.3

    @staticmethod
    def get_distance_squared(pos1: tuple[int, int], pos2: tuple[int, int]) -> int:
        return (pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2

    def create_terrain(self, per: op.OpenSimplex, size: tuple[int, int]) -> None:
        """ Cree grace au bruit de Perlin (Prelin's noise), sa deuxième version donc le Simplex,
        une carte avec de l'herbe, du sable et de l'eau
        :param per: L'objet nous permettant d'avoir les valeurs de chaque case (module opensimplex)
        :param size: taille de la carte (en blocks) en (x, y)
        """

        for y in range(size[1]):
            self.terrain.append([])
            for x in range(size[0]):
                # ici on utilise les plages de valeurs pour définir ce qu'il y a sur chaque case (basé sur le Simplex)
                tmp = per.noise2(x * 0.2, y * 0.2)
                if tmp < self.water_limit:
                    self.terrain[y].append(self.WATER)
                else:
                    self.terrain[y].append(self.GRASS)

        # ici on rajouter les blocks de sable à la place des blocks d'herbe
        for y, line in enumerate(self.terrain):
            for x, el in enumerate(line):
                # on remplace l'herbe dans un carré
                if el == self.WATER:
                    for i in range(x - BEACH_WIDTH, x + BEACH_WIDTH + 1):
                        for j in range(y - BEACH_WIDTH, y + BEACH_WIDTH + 1):
                            if 0 <= i < size[0] and 0 <= j < size[1]:
                                if self.terrain[j][i] == self.GRASS and \
                                        self.get_distance_squared((x, y), (i, j)) <= random.uniform(0, BEACH_WIDTH) ** 2:
                                    print("changed")
                                    self.terrain[j][i] = self.SAND

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

        self.create_terrain(self.per, size)


if __name__ == "__main__":
    screen = pygame.display.set_mode(SCREEN_SIZE)
    ter = Terrain(234, GRID_SIZE)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        screen.fill((0, 0, 0))

        for i, t in enumerate(ter.terrain):
            for j, c in enumerate(t):
                screen.blit(c, c.get_rect(topleft=(j * SIZE_BLOCK, i * SIZE_BLOCK)))

        pygame.display.update()
