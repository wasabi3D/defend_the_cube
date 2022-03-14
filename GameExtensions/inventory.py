import typing

import pygame

import GameExtensions.locals as loc
from GameManager.util import GameObject


# Classe pour les objets d'inventaire
class InventoryObject:
    def __init__(self, name: str, img: pygame.Surface, n: int, font: pygame.font.Font):
        self.name = name
        self.img = img
        self.n = n
        self.font = font
        self.n_img = font.render(str(self.n), False, loc.NUMBER_COLOR)
        self.max_n = loc.SPE_OBJ[self.name] if self.name in loc.SPE_OBJ else loc.MAX_OBJ

    def get_img(self) -> pygame.Surface:
        return self.img

    def get_name(self) -> str:
        return self.name

    def get_n(self) -> int:
        return self.n

    def get_n_img(self) -> pygame.Surface:
        return self.n_img

    def set_n(self, n: int):
        self.n = n
        self.n_img = self.font.render(str(self.n), False, loc.NUMBER_COLOR)

    def add_n(self, n: int):
        tmp = self.n
        self.n = min(self.n + n, self.max_n)
        self.n_img = self.font.render(str(self.n), False, loc.NUMBER_COLOR)
        return max(tmp + n - self.max_n, 0)

    def on_use(self):
        pass


# classe s'occupant de l'organiastion de l'inventaire
class Inventory(GameObject):
    is_pressed = {"bool": False, "inv_place": (0, 0)}
    is_shown = False
    was_open_inv_pressed = False
    selected = 0

    def __init__(self,
                 grid_size: tuple[int, int],
                 pos: pygame.Vector2,
                 image: pygame.Surface,
                 hot_bar_img: pygame.Surface,
                 selected_img: pygame.Surface,
                 name: str,
                 font: pygame.font.Font,
                 open_inv_key: int = pygame.K_e):
        self.size = loc.INV_IMG_SIZE
        self.h_size = loc.HOTBAR_IMG_SIZE
        self.font = font
        self.hotbar_img = pygame.transform.scale(hot_bar_img, self.h_size).convert_alpha()
        super().__init__(pos, 0, pygame.transform.scale(image, self.size).convert_alpha(), name)

        self.pos = pos
        self.hotbar_pos = pos + pygame.Vector2(abs(self.h_size[0] - self.size[0]) / 2 + loc.HOTBAR_POS_OFFSET[0],
                                               loc.HOTBAR_POS_OFFSET[1])

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

        self.selected_img = InventoryObject("selected", pygame.transform.scale(
            selected_img, (self.cell_size[0] +
                           2 * self.cell_offset[0],
                           self.cell_size[1] +
                           2 * self.cell_offset[1])).convert_alpha(), 1, self.font)

        self.side_offset = tuple([self.size[0] * loc.INV_GRID_OFFSET_PROP_TO_W[0] / loc.INV_GRID_OFFSET_PROP_TO_W[1]
                                  for _ in range(2)])
        self.total_offset = (self.side_offset[0] + pos.x,
                             self.side_offset[1] + pos.y)
        self.numb_offset = (self.cell_size[0] - self.cell_offset[0] - loc.NUMBER_SIZE[0],
                            self.cell_size[1] - self.cell_offset[1] - loc.NUMBER_SIZE[1])
        self.grid_size = grid_size[0], grid_size[1]
        self.inv_img_size = (self.cell_size[0] - 2 * self.cell_offset[0] + 1,
                             self.cell_size[0] - 2 * self.cell_offset[0] + 1)

        self.empty_cell = InventoryObject("empty", pygame.Surface((0, 0)), 1, self.font)
        self.objects = [[self.empty_cell for _ in range(grid_size[0])] for _ in range(grid_size[1])]
        self.hotbar = [self.empty_cell for _ in range(grid_size[0])]

        self.open_inv_key = open_inv_key

    def add_obj_at_pos(self, place: tuple[int, int], name: str, img: pygame.Surface, n: int) -> bool:
        """ Crée un objet d'inventaire et le met à une position définie
        :param place: coordonnées (x, y) de la place dans l'inventaire
        :param name: nom de l'objet
        :param img: image de l'objet
        :return: si la place était occupée ou non (dans quel cas il ne serait pas ajouté)
        """
        if place[0] < self.grid_size[0]:
            if self.objects[place[1]][place[0]] == self.empty_cell:
                self.objects[place[1]][place[0]] = InventoryObject(
                    name, pygame.transform.scale(img, self.inv_img_size).convert_alpha(), n, self.font
                )
                return True
        elif place[0] == self.grid_size[0]:
            if self.hotbar[place[0]] == self.empty_cell:
                self.hotbar[place[0]] = InventoryObject(
                    name, pygame.transform.scale(img, self.inv_img_size).convert_alpha(), n, self.font
                )
        else: return False

    def add_obj(self, name: str, img: pygame.Surface, n) -> bool:
        """ Rajoute un objet dans la première place disponoible
        :param name: nom de l'objet
        :param img: image de l'objet
        :return: si il a trouvé une place
        """
        return self.add_obj_ins(InventoryObject(
            name, pygame.transform.scale(img, self.inv_img_size).convert_alpha(), n, self.font
        ))

    def add_obj_ins(self, item: InventoryObject):
        """ Rajoute un objet dans la première place disponoible
        :param item: instance d'un objet
        :return: si il a trouvé une place
        """
        if not isinstance(item, InventoryObject):
            raise TypeError("Not an instance of inventory object.")

        # on remarquera que l'ordre de recherche est hotbar (gauhe-droite) puis inventaire (gauche-droite puis haut-bas)
        for i, el in enumerate(self.hotbar):
            if el == self.empty_cell:
                self.hotbar[i] = item
                return True
            elif el.get_name() == item.get_name():
                print("hi")
                self.hotbar[i].add_n(item.get_n())
                return True
        for y, line in enumerate(self.objects):
            for x, el in enumerate(line):
                if el == self.empty_cell:
                    self.objects[y][x] = item
                    return True
                elif el.get_name() == item.get_name():
                    print("hi_")
                    self.objects[y][x].add_n(item.get_n())
                    return True
        return False

    def move_obj(self, place1: tuple[int, int], place2: tuple[int, int], swap: bool = True) -> None:
        """ Bouge un objet dans l'inventaire
        :param place1: position (x, y) de l'objet à déplacer
        :param place2: position (x, y) de la place que l'objet veut occuper
        :param swap: si un objet occupe déjà la place les échanger ou ne pas le faire
        """
        # si il y a autant de conditions c'est parce qu'il y a toutes les combinations hotbar - inventaire
        if (swap or (self.objects[place2[1]][place2[0]] == self.empty_cell if place2[1] < self.grid_size[1] else
                     self.hotbar[place2[0]] == self.empty_cell)) and place1 != place2:
            if place1[1] < self.grid_size[1]:
                if place2[1] < self.grid_size[1]:
                    if self.objects[place1[1]][place1[0]].get_name() == self.objects[place2[1]][place2[0]].get_name():
                        tmp = self.objects[place2[1]][place2[0]].add_n(self.objects[place1[1]][place1[0]].get_n())
                        if tmp:
                            self.objects[place1[1]][place1[0]].set_n(tmp)
                        else:
                            self.objects[place1[1]][place1[0]] = self.empty_cell
                    else:
                        (self.objects[place1[1]][place1[0]],
                         self.objects[place2[1]][place2[0]]) = (self.objects[place2[1]][place2[0]],
                                                                self.objects[place1[1]][place1[0]])
                else:
                    if self.objects[place1[1]][place1[0]].get_name() == self.hotbar[place2[0]].get_name():
                        tmp = self.hotbar[place2[0]].add_n(self.objects[place1[1]][place1[0]].get_n())
                        if tmp:
                            self.objects[place1[1]][place1[0]].set_n(tmp)
                        else:
                            self.objects[place1[1]][place1[0]] = self.empty_cell
                    else:
                        (self.objects[place1[1]][place1[0]],
                         self.hotbar[place2[0]]) = (self.hotbar[place2[0]],
                                                    self.objects[place1[1]][place1[0]])
            else:
                if place2[1] < self.grid_size[1]:
                    if self.hotbar[place1[0]].get_name() == self.objects[place2[1]][place2[0]].get_name():
                        tmp = self.objects[place2[1]][place2[0]].add_n(self.hotbar[place1[0]].get_n())
                        if tmp:
                            self.hotbar[place1[0]].set_n(tmp)
                        else:
                            self.hotbar[place1[0]] = self.empty_cell
                    else:
                        (self.hotbar[place1[0]],
                         self.objects[place2[1]][place2[0]]) = (self.objects[place2[1]][place2[0]],
                                                                self.hotbar[place1[0]])
                else:
                    if self.hotbar[place1[0]].get_name() == self.hotbar[place2[0]].get_name():
                        tmp = self.hotbar[place2[0]].add_n(self.hotbar[place1[0]].get_n())
                        if tmp:
                            self.hotbar[place1[0]].set_n(tmp)
                        else:
                            self.hotbar[place1[0]] = self.empty_cell
                    else:
                        (self.hotbar[place1[0]],
                         self.hotbar[place2[0]]) = (self.hotbar[place2[0]],
                                                    self.hotbar[place1[0]])

    def get_obj(self, pos: tuple[int, int]) -> typing.Union[InventoryObject, None]:
        """ Nous donne l'objet présent dans la place donnée
        :param pos: position (x, y) qu'on veut avoir
        :return: l'objet présent à pos
        """
        if 0 <= pos[0] < self.objects[0].__len__() and 0 <= pos[1] < self.objects.__len__():
            if self.objects[pos[1]][pos[0]] == self.empty_cell:
                return
            else:
                return self.objects[pos[1]][pos[0]]
        elif 0 <= pos[0] < self.grid_size[0] and pos[1] == self.grid_size[1]:
            if self.hotbar[pos[0]] == self.empty_cell:
                return
            else:
                return self.hotbar[pos[0]]
        else:
            raise IndexError("The position was out of the inventory capacity")

    def early_update(self) -> None:
        """ Toutes les actions faites à chaque frame"""

        # Détéction de si on appuie sur le click gauche
        pressed_keys = pygame.key.get_pressed()
        mouse_but = pygame.mouse.get_pressed(5)
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
                get_hotbar_mouse_co = get_grid_mouse_co - loc.HOTBAR_POS_OFFSET
                grid_cell = (int(get_grid_mouse_co.x // self.cell_size[0]),
                             int(get_grid_mouse_co.y // self.cell_size[1]))
                hotbar_cell = (int(get_hotbar_mouse_co.x // self.cell_size[0]),
                               int(get_hotbar_mouse_co.y // self.cell_size[1]))

                # au final on ne vérifie plus que si les coordonnées de reçues font partie de l'inventaire
                if 0 <= grid_cell[0] < self.grid_size[0] and 0 <= grid_cell[1] < self.grid_size[1]:
                    if self.get_obj(grid_cell) is not None:
                        self.is_pressed["inv_place"] = grid_cell
                        self.is_pressed["bool"] = True
                elif 0 <= hotbar_cell[0] < self.grid_size[0] and not hotbar_cell[1]:
                    if self.get_obj((hotbar_cell[0], self.grid_size[1])) is not None:
                        self.is_pressed["inv_place"] = hotbar_cell[0], self.grid_size[1]
                        self.is_pressed["bool"] = True

            # si on arrète d'appuyer sur le click gauche (et qu'on avait un objet)
            # le procécus des coordonnées est le même que celui d'en haut
            elif not mouse_but[0] and self.is_pressed["bool"]:
                mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
                get_grid_mouse_co = mouse_pos - self.side_offset - self.pos
                get_hotbar_mouse_co = get_grid_mouse_co - loc.HOTBAR_POS_OFFSET
                grid_cell = (int(get_grid_mouse_co.x // self.cell_size[0]),
                             int(get_grid_mouse_co.y // self.cell_size[1]))
                hotbar_cell = (int(get_hotbar_mouse_co.x // self.cell_size[0]),
                               int(get_hotbar_mouse_co.y // self.cell_size[1]))

                if 0 <= grid_cell[0] < self.grid_size[0] and 0 <= grid_cell[1] < self.grid_size[1]:
                    self.is_pressed["bool"] = False
                    self.move_obj(self.is_pressed["inv_place"], grid_cell)
                elif 0 <= hotbar_cell[0] < self.grid_size[0] and not hotbar_cell[1]:
                    self.is_pressed["bool"] = False
                    self.move_obj(self.is_pressed["inv_place"], (hotbar_cell[0], self.grid_size[1]))

        if not self.is_shown:
            # for event in pygame.event.get():
            #     if event.type == pygame.MOUSEBUTTONDOWN:
            #         if event.button == 4:
            #             self.selected = self.selected + 1 if self.selected + 1 < self.grid_size[0] else 0
            #         if event.button == 5:
            #             self.selected = self.selected - 1 if self.selected - 1 >= 0 else self.grid_size[0] - 1
            if mouse_but[0]:
                mouse_pos = pygame.Vector2(*pygame.mouse.get_pos())

                # on convertis les coordonnées de la souris en coordonnées de l'inventaire
                get_hotbar_mouse_co = mouse_pos - self.side_offset - self.pos - loc.HOTBAR_POS_OFFSET
                hotbar_cell = (int(get_hotbar_mouse_co.x // self.cell_size[0]),
                               int(get_hotbar_mouse_co.y // self.cell_size[1]))

                if 0 <= hotbar_cell[0] < self.grid_size[0] and not hotbar_cell[1]:
                    self.selected = hotbar_cell[0]

                elif not self.is_pressed["bool"]:
                    self.hotbar[self.selected].on_use()
                    self.is_pressed["bool"] = True
            elif self.is_pressed["bool"]:
                self.is_pressed["bool"] = False

    def blit_cell(self, screen: pygame.Surface, pos: tuple[int, int], el: InventoryObject) -> None:
        """ Faire afficher un objet à se place dans la grille
        :param screen: fenêtre du jeu
        :param pos: la place de l'objet qu'on veut faire apparaitre
        :param el: l'element qu'on veut faire apparaitre
        """
        x, y = pos

        # si la cellule est dans l'inventaire
        if y != self.grid_size[1]:
            pos = (
                x * self.cell_size[0] + self.total_offset[0] + self.cell_offset[0],
                y * self.cell_size[1] + self.total_offset[1] + self.cell_offset[1]
            )
            screen.blit(
                el.get_img(),
                el.get_img().get_rect(topleft=pos)
            )
            screen.blit(
                el.get_n_img(),
                el.get_n_img().get_rect(topleft=(pos[0] + self.numb_offset[0], pos[1] + self.numb_offset[1]))
            )
        # si la cellule est dans la hotbar
        else:
            pos = (
                x * self.cell_size[0] + self.total_offset[0] +
                self.cell_offset[0] + loc.HOTBAR_CELL_IMPERFECTION[0] + loc.HOTBAR_POS_OFFSET[0],
                loc.HOTBAR_POS_OFFSET[1] + self.cell_size[0] + loc.HOTBAR_CELL_IMPERFECTION[1]
            )
            screen.blit(
                el.get_img(),
                el.get_img().get_rect(topleft=pos)
            )
            screen.blit(
                el.get_n_img(),
                el.get_n_img().get_rect(topleft=(pos[0] + self.numb_offset[0], pos[1] + self.numb_offset[1]))
            )

    def blit(self, screen: pygame.Surface, apply_alpha=True) -> None:
        """ affiche l'inventaire
        :param screen: fenêtre du jeu
        """

        # Affichage de la hotbar
        screen.blit(self.hotbar_img, self.hotbar_img.get_rect(topleft=self.hotbar_pos))
        screen.blit(self.selected_img.get_img(),
                    self.selected_img.get_img().get_rect(topleft=(
                        self.selected * self.cell_size[0] + self.total_offset[0]
                        + loc.HOTBAR_CELL_IMPERFECTION[0] + loc.HOTBAR_POS_OFFSET[0] - self.cell_offset[0],
                        loc.HOTBAR_POS_OFFSET[1] + self.cell_size[1] - 2 * self.cell_offset[1] + 0.3
                    )))
        for i, el in enumerate(self.hotbar):
            if el != self.empty_cell and not (self.is_pressed["inv_place"] == (i, self.grid_size[1])
                                              and self.is_pressed["bool"]):
                self.blit_cell(screen, (i, self.grid_size[1]), el)

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
                el = self.get_obj(self.is_pressed["inv_place"])
                pos = pygame.mouse.get_pos()
                screen.blit(el.get_img(), el.get_img().get_rect(center=pos))
                screen.blit(
                    el.get_n_img(),
                    el.get_n_img().get_rect(center=(pos[0] + self.numb_offset[0] / 2, pos[1] + self.numb_offset[1] / 2))
                )
