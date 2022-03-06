import typing

import pygame

import GameExtensions.locals as loc
from GameManager.util import GameObject


# Classe pour les objets d'inventaire
class InventoryObject:
    def __init__(self, name: str, img: pygame.Surface):
        self.name = name
        self.img = img

    def get_img(self):
        return self.img

    def get_name(self):
        return self.name


# classe pour les objets utilisables (affiché même quand l'invemtaire est fermé)
class Hotbar:
    def __init__(self, img):
        pass


# classe s'occupant de l'organiastion de l'inventaire
class Inventory(GameObject):
    is_pressed = {"bool": False, "inv_place": (0, 0)}
    is_shown = False
    was_open_inv_pressed = False

    def __init__(self,
                 grid_size: tuple[int, int],
                 pos: pygame.Vector2,
                 image: pygame.Surface,
                 name: str,
                 open_inv_key: int = pygame.K_e):
        self.size = loc.INV_IMG_SIZE
        super().__init__(pos, 0, pygame.transform.scale(image, self.size).convert_alpha(), name)
        self.pos = pos
        self.cell_offset = tuple([
            self.size[0] * loc.INV_CELL_OFFSET_TO_W[0] / loc.INV_CELL_OFFSET_TO_W[1]
            + loc.INV_CELL_OFFSET_TO_W[2]
            for _ in range(2)
        ])
        self.cell_size = tuple([
            self.size[0] * loc.INV_CELL_SIZE_PROP_TO_W[0] / loc.INV_CELL_SIZE_PROP_TO_W[1] - self.cell_offset[0]
            + loc.INV_CELL_SIZE_PROP_TO_W[2]
            for _ in range(2)
        ])
        self.side_offset = tuple([self.size[0] * loc.INV_GRID_OFFSET_PROP_TO_W[0] / loc.INV_GRID_OFFSET_PROP_TO_W[1]
                                  for _ in range(2)])
        self.total_offset = (self.side_offset[0] + pos.x,
                             self.side_offset[1] + pos.y)
        self.grid_size = grid_size
        self.inv_img_size = (self.cell_size[0] - 2 * self.cell_offset[0] + 1,
                             self.cell_size[0] - 2 * self.cell_offset[0] + 1)

        self.empty_cell = InventoryObject("empty", pygame.Surface((0, 0)))
        self.objects = [[self.empty_cell for _ in range(grid_size[0])] for _ in range(grid_size[1])]

        self.open_inv_key = open_inv_key

    def add_obj_at_pos(self, place: tuple[int, int], name: str, img: pygame.Surface) -> bool:
        """ Crée un objet d'inventaire et le met à une position définie
        :param place: coordonnées (x, y) de la place dans l'inventaire
        :param name: nom de l'objet
        :param img: image de l'objet
        :return: si la place était occupée ou non (dans quel cas il ne serait pas ajouté)
        """
        if self.objects[place[1]][place[0]] == self.empty_cell:
            self.objects[place[1]][place[0]] = InventoryObject(name, pygame.transform.scale(img, self.inv_img_size))
            return True
        else: return False

    def add_obj(self, name: str, img: pygame.Surface) -> bool:
        """ Rajoute un objet dans la première place disponoible
        :param name: nom de l'objet
        :param img: image de l'objet
        :return: si il a trouvé une place
        """
        for y, line in enumerate(self.objects):
            for x, el in enumerate(line):
                if el == self.empty_cell:
                    self.objects[y][x] = InventoryObject(name,
                                                         pygame.transform.scale(img, self.inv_img_size).convert_alpha())
                    return True
        return False

    def move_obj(self, place1: tuple[int, int], place2: tuple[int, int], swap: bool = True) -> None:
        """ Bouge un objet dans l'inventaire
        :param place1: position (x, y) de l'objet à déplacer
        :param place2: position (x, y) de la place que l'objet veut occuper
        :param swap: si un objet occupe déjà la place les échanger ou ne pas le faire
        """
        if swap:
            (self.objects[place1[1]][place1[0]],
             self.objects[place2[1]][place2[0]]) = (self.objects[place2[1]][place2[0]],
                                                    self.objects[place1[1]][place1[0]])
        elif self.objects[place2[1]][place2[0]] == self.empty_cell:
            (self.objects[place1[1]][place1[0]],
             self.objects[place2[1]][place2[0]]) = (self.objects[place2[1]][place2[0]],
                                                    self.objects[place1[1]][place1[0]])

    def get_obj(self, pos: tuple[int, int]) -> typing.Union[InventoryObject, None]:
        """ Nous donne l'objet présent dans la place donnée
        :param pos: position (x, y) qu'on veut avoir
        :return: l'objet présent à pos
        """
        if 0 <= pos[0] < self.objects[0].__len__() and 0 <= pos[1] < self.objects.__len__():
            if self.objects[pos[1]][pos[0]] == self.empty_cell: return
            else: return self.objects[pos[1]][pos[0]]
        else:
            raise IndexError("The position was out of the inventory capacity")

    def early_update(self) -> None:
        """ Toutes les actions faites à chaque frame"""

        # Détéction de si on appuie sur le click gauche
        pressed_keys = pygame.key.get_pressed()
        mouse_but = pygame.mouse.get_pressed()
        if not self.was_open_inv_pressed and pressed_keys[self.open_inv_key]:
            self.is_shown = not self.is_shown
            self.was_open_inv_pressed = True

        if not pressed_keys[self.open_inv_key] and self.was_open_inv_pressed:
            self.was_open_inv_pressed = False

        # On détecte les cases sur les quelles on appuie
        if self.is_shown:
            # si on à appuyé sur le click gauche
            if mouse_but[0] and not self.is_pressed["bool"]:
                mouse_pos = pygame.Vector2(*pygame.mouse.get_pos())

                # on convertis les coordonnées de la souris en coordonnées de l'inventaire
                get_grid_mouse_co = mouse_pos - self.side_offset - self.pos
                grid_cell = int(get_grid_mouse_co.x // self.cell_size[0]), int(get_grid_mouse_co.y // self.cell_size[1])

                # au final on ne vérifie plus que si les coordonnées de reçues font partie de l'inventaire
                if 0 <= grid_cell[0] < self.grid_size[0] and 0 <= grid_cell[1] < self.grid_size[1]:
                    if self.get_obj(grid_cell) is not None:
                        self.is_pressed["inv_place"] = grid_cell
                        self.is_pressed["bool"] = True

            # si on arrète d'appuyer sur le click gauche (et qu'on avait un objet)
            # le procécus des coordonnées est le même que celui d'en haut
            elif not mouse_but[0] and self.is_pressed["bool"]:
                mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
                get_grid_mouse_co = mouse_pos - self.side_offset - self.pos
                grid_cell = int(get_grid_mouse_co.x // self.cell_size[0]), int(get_grid_mouse_co.y // self.cell_size[1])
                if 0 <= grid_cell[0] < self.grid_size[0] and 0 <= grid_cell[1] < self.grid_size[1]:
                    self.is_pressed["bool"] = False
                    self.move_obj(self.is_pressed["inv_place"], grid_cell)

    def blit_cell(self, screen: pygame.Surface, pos: tuple[int, int], el: InventoryObject) -> None:
        """ Faire afficher un objet à se place dans la grille
        :param screen: fenêtre du jeu
        :param pos: la place de l'objet qu'on veut faire apparaitre
        :param el: l'element qu'on veut faire apparaitre
        """
        x, y = pos
        screen.blit(
            el.get_img(),
            el.get_img().get_rect(topleft=(
                x * self.cell_size[0] + self.total_offset[0] + self.cell_offset[0],
                y * self.cell_size[1] + self.total_offset[1] + self.cell_offset[1]))
        )

    def blit(self, screen: pygame.Surface) -> None:
        """ affiche l'onventaire
        :param screen: fenêtre du jeu
        """
        if self.is_shown:
            screen.blit(self.image, self.image.get_rect(topleft=self.pos))
            for y, line in enumerate(self.objects):
                for x, el in enumerate(line):
                    if "empty" != el.get_name():
                        # on n'affiche pas directement l'objet déplacé
                        if not ((x, y) == self.is_pressed["inv_place"] and self.is_pressed["bool"]):
                            self.blit_cell(screen, (x, y), el)
            # on affiche l'objet déplacé ici pour qu'il se retrouve devant
            if self.is_pressed["bool"]:
                el = self.objects[self.is_pressed["inv_place"][1]][self.is_pressed["inv_place"][0]]
                screen.blit(el.get_img(), el.get_img().get_rect(center=pygame.mouse.get_pos()))
