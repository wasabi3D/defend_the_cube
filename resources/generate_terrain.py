import opensimplex as op
import pygame


pygame.init()
GRID_SIZE = 20


class Terrain:
    terrain = []
    water_limit = 0.2
    sand_limit = 0.25

    def create_terrain(self, per: op.OpenSimplex, size: tuple[int, int]) -> None:
        def simple_curve(val: float) -> float:
            end, start = 0.6, 0.4
            return 0 if val < start else 1 if val > end else 1 / (end - start)

        def plains(perp: op.OpenSimplex, x, y) -> float:
            return perp.noise2(x * 0.1, y * 0.1) ** 0.25 - 0.6

        def mountains(perp: op.OpenSimplex, x, y) -> float:
            return 2 * perp.noise2(x * 0.5, y * 0.4)

        self.terrain = [[per.noise2(x*0.2, y*0.2) for x in range(size[0])] for y in range(size[1])]

        for i, el in enumerate(self.terrain):
            for i2, el2 in enumerate(el):
                if el2 < self.water_limit:
                    self.terrain[i][i2] = self.WATER
                elif el2 < self.sand_limit:
                    self.terrain[i][i2] = self.SAND
                else:
                    self.terrain[i][i2] = self.GRASS

    def __init__(self, seed: int, size: tuple[int, int]) -> None:
        self.seed = seed
        self.per = op.OpenSimplex(seed)

        d = r"C:\Users\louis\PycharmProjects\NSI_projet2\resources\test\grid"
        self.GRASS = pygame.transform.scale(pygame.image.load(d + r"\grid_two.png"), (GRID_SIZE, GRID_SIZE))
        self.SAND = pygame.transform.scale(pygame.image.load(d + r"\grid_one.png"), (GRID_SIZE, GRID_SIZE))
        self.WATER = pygame.transform.scale(pygame.image.load(d + r"\grid_three.png"), (GRID_SIZE, GRID_SIZE))

        self.create_terrain(self.per, size)


if __name__ == "__main__":
    screen = pygame.display.set_mode((500, 500))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        screen.fill((0, 0, 0))
        pygame.display.update()
