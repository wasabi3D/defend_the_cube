""" Organisation de l'inventaire """
import typing
import pygame
import GameExtensions.locals as loc
from GameManager.util import GameObject
import GameExtensions.items as items
import GameManager.singleton as sing


class Inventory(GameObject):
    """classe s'occupant de l'organiastion de l'inventaire """
    is_shown = False
    was_open_inv_pressed = False
    selected = 0

    def __init__(self,
                 grid_size: tuple[int, int],
                 pos: pygame.Vector2,
                 image: pygame.Surface,
                 hot_bar_img: pygame.Surface,
                 craft_img: pygame.Surface,
                 selected_img: pygame.Surface,
                 name: str,
                 font: pygame.font.Font,
                 open_inv_key: int = pygame.K_e):
        self.size = loc.INV_IMG_SIZE
        self.h_size = loc.HOTBAR_IMG_SIZE
        self.c_size = loc.CRAFT_IMG_SIZE
        self.font = font
        self.hotbar_img = pygame.transform.scale(hot_bar_img, self.h_size).convert_alpha()
        self.craft_img = pygame.transform.scale(craft_img, self.c_size).convert_alpha()
        super().__init__(pos, 0, pygame.transform.scale(image, self.size).convert_alpha(), name)

        self.pos = pos
        self.hotbar_pos = pos + pygame.Vector2(abs(self.h_size[0] - self.size[0]) / 2 + loc.HOTBAR_POS_OFFSET[0],
                                               loc.HOTBAR_POS_OFFSET[1])
        self.craft_pos = pos + pygame.Vector2(*loc.CRAFT_POS_OFFSET)

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

        self.selected_img = items.InventoryObject("selected", pygame.transform.scale(
            selected_img, (self.cell_size[0] +
                           2 * self.cell_offset[0],
                           self.cell_size[1] +
                           2 * self.cell_offset[1])).convert_alpha(), 1, self.font)

        self.side_offset = (
            self.size[0] * loc.INV_GRID_OFFSET_PROP_TO_W[0] / loc.INV_GRID_OFFSET_PROP_TO_W[1],
            self.size[0] * loc.INV_GRID_OFFSET_PROP_TO_W[0] / loc.INV_GRID_OFFSET_PROP_TO_W[1]
        )
        self.total_offset = (self.side_offset[0] + pos.x,
                             self.side_offset[1] + pos.y)
        self.numb_offset = (self.cell_size[0] - self.cell_offset[0] - loc.NUMBER_SIZE[0],
                            self.cell_size[1] - self.cell_offset[1] - loc.NUMBER_SIZE[1])
        self.grid_size = grid_size[0], grid_size[1]
        self.inv_img_size = (self.cell_size[0] - 2 * self.cell_offset[0] + 1,
                             self.cell_size[0] - 2 * self.cell_offset[0] + 1)
        self.empty_cell = items.InventoryObject(loc.EMPTY, pygame.Surface((0, 0)), 1, self.font)
        self.is_pressed = {"bool": False,
                           "bool_right": False,
                           "cary_list": ([self.empty_cell], 0),
                           "cary": self.empty_cell,
                           "crafted": False}
        self.objects = [[self.empty_cell for _ in range(grid_size[0])] for _ in range(grid_size[1])]
        self.hotbar: list[items.InventoryObject] = [self.empty_cell for _ in range(grid_size[0])]
        self.crafting_station: tuple[list[list[items.InventoryObject]], list[items.InventoryObject]] = (
            [[self.empty_cell for _ in range(3)] for _ in range(3)],
            [self.empty_cell])
        self.recipes = items.get_recipes()

        self.open_inv_key = open_inv_key

    def add_obj_at_pos(self, place: tuple[int, int], name: str, img: pygame.Surface, n: int) -> bool:
        """ Crée un objet d'inventaire et le met à une position définie
        :param place: coordonnées (x, y) de la place dans l'inventaire
        :param name: nom de l'objet
        :param img: image de l'objet
        :param n: quantité de cet objet ajouté
        :return: si la place était occupée ou non (dans quel cas il ne serait pas ajouté)
        """
        return self.add_obj_ins_at_place(
            place, items.InventoryObject(
                name, pygame.transform.scale(img, self.inv_img_size).convert_alpha(), n, self.font
            )
        )

    def add_obj(self, name: str, img: pygame.Surface, n: int) -> bool:
        """ Rajoute un objet dans la première place disponoible
        :param name: nom de l'objet
        :param img: image de l'objet
        :param n: quantité de cet objet à ajouter dans l'inventaire
        :return: si il a trouvé une place
        """
        return self.add_obj_ins(items.InventoryObject(
            name, pygame.transform.scale(img, self.inv_img_size).convert_alpha(), n, self.font
        ))

    def add_obj_ins_empty_place(self, item: items.InventoryObject):
        """ Rajoute un objet dans la première place disponoible vide
        :param item: instance d'un objet
        :return: si il a trouvé une place
        """
        if not isinstance(item, items.InventoryObject):
            raise TypeError("Not an instance of inventory object.")

        # on remarquera que l'ordre de recherche est hotbar (gauhe-droite) puis inventaire (gauche-droite puis haut-bas)
        for i, el in enumerate(self.hotbar):
            if el == self.empty_cell:
                self.hotbar[i] = item
                return True
        for y, line in enumerate(self.objects):
            for x, el in enumerate(line):
                if el == self.empty_cell:
                    self.objects[y][x] = item
                    return True

    def add_obj_ins_at_place(self, place: tuple[int, int], item: items.InventoryObject) -> bool:
        """ Inserer un objet à un endroit précis
        :param place: coordonées dans l'inventaire à placer
        :param item: l'objet en question
        :return: si l'objet avait de la place ou pas
        """
        if place[1] < self.grid_size[1] and place[0] < self.grid_size[0]:  # si l'objet est dans l'invntaire
            if self.objects[place[1]][place[0]] == self.empty_cell:
                self.objects[place[1]][place[0]] = item
                return True
            elif self.objects[place[1]][place[0]].get_name() == item.get_name():
                if self.objects[place[1]][place[0]].get_n() + item.get_n() <= item.max_n:
                    self.objects[place[1]][place[0]].add_n(item.get_n())
                    return True
                else:
                    return False
        elif place[1] == self.grid_size[1]:  # si les coordonnées donnent dans la hotbar est dans la hotbar
            if self.hotbar[place[0]] == self.empty_cell:
                self.hotbar[place[0]] = item
                return True
            elif self.hotbar[place[0]].get_name() == item.get_name():
                if self.hotbar[place[0]].get_n() + item.get_n() <= item.max_n:
                    self.hotbar[place[0]].add_n(item.get_n())
                    return True
                else:
                    return False
        elif place[0] - self.grid_size[0] < 3 and place[1] < 3:
            if self.crafting_station[0][place[1]][place[0] - self.grid_size[0]] == self.empty_cell:
                self.crafting_station[0][place[1]][place[0] - self.grid_size[0]] = item
                return True
            elif self.crafting_station[0][place[1]][place[0] - self.grid_size[0]].get_n() + item.get_n() <= item.max_n:
                self.crafting_station[0][place[1]][place[0] - self.grid_size[0]].add_n(item.get_n())
                return True
            else:
                return False
        return False  # si il n'y a pas de place dans la cellule indiquée

    def add_obj_ins(self, item: items.InventoryObject) -> bool:
        """ Rajoute un objet dans la première place disponoible dans laquelle il est possible de le mettre
        :param item: instance d'un objet
        :return: si il a trouvé une place
        """
        if not isinstance(item, items.InventoryObject):
            raise TypeError("Not an instance of inventory object.")

        # on remarquera que l'ordre de recherche est hotbar (gauhe-droite) puis inventaire (gauche-droite puis haut-bas)
        for i, el in enumerate(self.hotbar):
            if el.get_name() == item.get_name():
                rest = self.hotbar[i].add_n(item.get_n())
                if rest:
                    item = item.copy()
                    item.set_n(rest)
                else: return True
        for y, line in enumerate(self.objects):
            for x, el in enumerate(line):
                if el.get_name() == item.get_name():
                    rest = self.objects[y][x].add_n(item.get_n())
                    if rest:
                        item = item.copy()
                        item.set_n(rest)
                    else: return True
        return self.add_obj_ins_empty_place(item)

    def get_what_menu(self, co: tuple[int, int], get_result: bool = True) -> tuple[list[items.InventoryObject], int]:
        """Nous rend le menu et la ligne dans lequel sont les coordonnées"""
        if 0 <= co[0] < self.grid_size[0] and 0 <= co[1] < self.grid_size[1]:
            return self.objects[co[1]], co[0]
        elif co[1] == self.grid_size[1]:
            return self.hotbar, co[0]
        elif self.grid_size[0] <= co[0] < self.grid_size[0] + 3 and 0 <= co[1] < 3:
            return self.crafting_station[0][co[1]], co[0] - self.grid_size[0]
        elif co[0] == self.grid_size[0] + 4 and co[1] == 1:
            if get_result:
                return self.crafting_station[1], 0
            else:
                return [self.empty_cell], 0
        else:
            raise IndexError("The coordinates where out of the inventory capacity")

    def move_obj(self, place1: tuple[int, int], place2: tuple[int, int], swap: bool = False) -> None:
        """ Bouge un objet dans l'inventaire
        :param place1: position (x, y) de l'objet à déplacer
        :param place2: position (x, y) de la place que l'objet veut occuper
        :param swap: si un objet occupe déjà la place les échanger ou ne pas le faire
        """

        o1 = self.get_what_menu(place1)
        el1 = o1[0][o1[1]]
        o2 = self.get_what_menu(place2)
        el2 = o2[0][o2[1]]

        if el1.get_name() == el2.get_name() and not swap:
            tmp = el2.add_n(el1.get_n())
            if tmp:
                el1.set_n(tmp)
            else:
                o1[0][o1[1]] = self.empty_cell
        else:
            o1[0][o1[1]], o2[0][o2[1]] = o2[0][o2[1]], o1[0][o1[1]]

    def get_obj(self, pos: tuple[int, int]) -> typing.Union[items.InventoryObject, None]:
        """ Nous donne l'objet présent dans la place donnée
        :param pos: position (x, y) qu'on veut avoir
        :return: l'objet présent à pos
        """
        o1 = self.get_what_menu(pos)
        el = o1[0][o1[1]]
        return el
        # if 0 <= pos[0] < self.objects[0].__len__() and 0 <= pos[1] < self.objects.__len__():
        #     if self.objects[pos[1]][pos[0]] == self.empty_cell:
        #         return
        #     else:
        #         return self.objects[pos[1]][pos[0]]
        # elif 0 <= pos[0] < self.grid_size[0] and pos[1] == self.grid_size[1]:
        #     if self.hotbar[pos[0]] == self.empty_cell:
        #         return
        #     else:
        #         return self.hotbar[pos[0]]
        # elif self.grid_size[0] <= pos[0] < self.grid_size[0] + 3 and 0 <= pos[1] < 3 and self.is_shown:
        #     if self.crafting_station[0][pos[1]][pos[0] - self.grid_size[0]] == self.empty_cell:
        #         return
        #     else:
        #         return self.crafting_station[0][pos[1]][pos[0] - self.grid_size[0]]
        # elif pos[0] == self.grid_size[0] + 4 and pos[1] == 1:
        #     if self.crafting_station[1][0] == self.empty_cell:
        #         return
        #     else:
        #         return self.crafting_station[1][0]
        # else:
        #     raise IndexError("The position was out of the inventory capacity")

    def try_recipe(self):
        """fonction permettant de vérifier si on à la possibilité de crafter un objet"""
        # noinspection PyTypeChecker
        tested_recipe: tuple[tuple[str, str, str],
                             tuple[str, str, str],
                             tuple[str, str, str]] = tuple(
            map(lambda x: tuple(
                map(lambda x2: x2.get_name(), x)), self.crafting_station[0]
                )
        )

        if tested_recipe in self.recipes:
            tmp = self.recipes[tested_recipe]
            self.crafting_station[1][0] = tmp[0](tmp[1], self.font)
        else:
            self.crafting_station[1][0] = self.empty_cell

    def recuperate_recipe(self):
        """fonction permettant de récupérér l'objet à crafter"""
        for i, line in enumerate(self.crafting_station[0]):
            for j, el in enumerate(line):
                if el.get_name() != "empty":
                    if not el.remove_one():
                        self.crafting_station[0][i][j] = self.empty_cell
        self.add_obj_ins(self.crafting_station[1][0])
        self.crafting_station[1][0] = self.empty_cell

    def early_update(self) -> None:
        """ Toutes les actions faites à chaque frame"""

        # Détéction de si on appuie sur la souris ou le clavier
        pressed_keys = pygame.key.get_pressed()
        all_mouse_but = pygame.mouse.get_pressed(5)
        mouse_but = (all_mouse_but[0], all_mouse_but[2])
        if not self.was_open_inv_pressed and pressed_keys[self.open_inv_key]:
            self.is_shown = not self.is_shown
            self.was_open_inv_pressed = True
            for line in self.crafting_station[0]:
                for el in line:
                    if el != self.empty_cell:
                        self.add_obj_ins(el)
            self.crafting_station = (
                [[self.empty_cell for _ in range(3)] for _ in range(3)],
                [self.empty_cell]
            )

        if not pressed_keys[self.open_inv_key] and self.was_open_inv_pressed:
            self.was_open_inv_pressed = False

        # On détecte les cases sur les quelles on appuie
        if self.is_shown:
            # si on à appuyé sur le click gauche
            final_cos: typing.Union[None, tuple[int, int]] = None
            # On vérifie en premier si on a appuyé ou laché (suelement une fois) un des boutons de la souris
            if ((any(mouse_but) and not self.is_pressed["bool"] and not self.is_pressed["bool_right"]) or
                    (not any(mouse_but) and (self.is_pressed["bool"] or self.is_pressed["bool_right"])))\
                    and not self.is_pressed["crafted"]:
                # On pourra avoir ducoup les coordonnées des positions
                # de la souris transformées en coordonées d'"inventaire"

                # On commence par donner les coordonnées de la souris dans chaque élément de l'inventaire
                mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
                get_grid_mouse_co = mouse_pos - self.side_offset - self.pos
                get_hotbar_mouse_co = get_grid_mouse_co - loc.HOTBAR_POS_OFFSET
                get_craft_mouse_co = get_grid_mouse_co - loc.CRAFT_POS_OFFSET
                grid_cell = (int(get_grid_mouse_co.x // self.cell_size[0]),
                             int(get_grid_mouse_co.y // self.cell_size[1]))
                hotbar_cell = (int(get_hotbar_mouse_co.x // self.cell_size[0]),
                               int(get_hotbar_mouse_co.y // self.cell_size[1]))
                craft_cell = (int(get_craft_mouse_co.x // self.cell_size[0]),
                               int(get_craft_mouse_co.y // self.cell_size[1]))
                # puis on transcrit en coordonnées dans l'inventaire
                if 0 <= grid_cell[0] < self.grid_size[0] and 0 <= grid_cell[1] < self.grid_size[1]:
                    final_cos = grid_cell
                elif 0 <= hotbar_cell[0] < self.grid_size[0] and not hotbar_cell[1]:
                    final_cos = hotbar_cell[0], self.grid_size[1]
                elif 0 <= craft_cell[0] < 3 > craft_cell[1] >= 0:
                    final_cos = craft_cell[0] + self.grid_size[0], craft_cell[1]
                elif craft_cell == (4, 1) and any(mouse_but) and any(mouse_but):
                    self.recuperate_recipe()
                    self.is_pressed["bool"] = True
                    self.is_pressed["crafted"] = True
            if final_cos is not None:
                # si on a eu des coordonées, on en arrivera ici
                ol = self.get_what_menu(final_cos)  # ol pour "object list"
                fo = ol[0][ol[1]]  # fo pour "final object"
                if fo != self.empty_cell and any(mouse_but):
                    self.is_pressed["cary"] = fo.copy()
                    self.is_pressed["cary_list"] = ol
                    if mouse_but[0]:  # actions si ou a appuyé sur le click gauche
                        self.is_pressed["bool"] = True
                        ol[0][ol[1]] = self.empty_cell
                    elif mouse_but[1]:  # actions si on a appuyé su le click droit
                        tmp = fo.get_n()
                        tmp1 = tmp // 2
                        tmp -= tmp1
                        self.is_pressed["cary"].set_n(tmp)
                        if tmp:
                            fo.set_n(tmp1)
                        else:
                            ol[0][ol[1]] = self.empty_cell
                        self.is_pressed["bool_right"] = True
                elif not any(mouse_but):  # Finalement, action si on à relaché un des clicks
                    if self.is_pressed["bool_right"]:
                        if fo == self.empty_cell:
                            ol[0][ol[1]] = self.is_pressed["cary"]
                            self.is_pressed["bool_right"] = False
                        elif self.is_pressed["cary"].get_name() == fo.get_name():
                            tmp = fo.add_n(self.is_pressed["cary"].get_n())
                            if tmp:
                                self.is_pressed["cary_list"][0][self.is_pressed["cary_list"][1]].add_n(tmp)
                            self.is_pressed["bool_right"] = False
                    else:
                        if fo == self.empty_cell:
                            ol[0][ol[1]] = self.is_pressed["cary"]
                        elif self.is_pressed["cary"].get_name() == fo.get_name():
                            tmp = fo.add_n(self.is_pressed["cary"].get_n())
                            if tmp:
                                tmp2 = fo.copy()
                                tmp2.set_n(tmp)
                                self.is_pressed["cary_list"][0][self.is_pressed["cary_list"][1]] = tmp2
                        else:
                            (ol[0][ol[1]],
                             self.is_pressed["cary_list"][0][self.is_pressed["cary_list"][1]]) = (
                                self.is_pressed["cary"], fo)
                        self.is_pressed["bool"] = False
            if self.is_pressed["bool"] and self.is_pressed["crafted"] and not any(mouse_but):
                self.is_pressed["bool"], self.is_pressed["crafted"] = False, False
            self.try_recipe()

        if not self.is_shown:
            if mouse_but[0]:
                mouse_pos = pygame.Vector2(*pygame.mouse.get_pos())

                # on convertis les coordonnées de la souris en coordonnées de l'inventaire
                get_hotbar_mouse_co = mouse_pos - self.side_offset - self.pos - loc.HOTBAR_POS_OFFSET
                hotbar_cell = (int(get_hotbar_mouse_co.x // self.cell_size[0]),
                               int(get_hotbar_mouse_co.y // self.cell_size[1]))

                if 0 <= hotbar_cell[0] < self.grid_size[0] and not hotbar_cell[1]:
                    self.selected = hotbar_cell[0]

                elif not self.is_pressed["bool"] and not sing.ROOT.game_objects["player"].ghost_mode:
                    if not self.hotbar[self.selected].on_use():
                        self.hotbar[self.selected] = self.empty_cell
                    self.is_pressed["bool"] = True
            elif self.is_pressed["bool"]:
                self.is_pressed["bool"] = False

    def blit_cell(self, screen: pygame.Surface, pos: tuple[int, int], el: items.InventoryObject) -> None:
        """ Faire afficher un objet à se place dans la grille
        :param screen: fenêtre du jeu
        :param pos: la place de l'objet qu'on veut faire apparaitre
        :param el: l'element qu'on veut faire apparaitre
        """
        x, y = pos

        # si la cellule est dans l'inventaire
        if 0 <= y < self.grid_size[1] and 0 <= x < self.grid_size[0]:
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
        elif 0 <= x < self.grid_size[0]:
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
        else:  # Finalement si elle est dans le menu de craft en supposant qu'on ne s'est pas trompé
            x -= self.grid_size[0]
            pos = (
                x * self.cell_size[0] + self.total_offset[0] +
                self.cell_offset[0] + loc.CRAFT_CELL_IMPERFECTION[0] + loc.CRAFT_POS_OFFSET[0],
                y * self.cell_size[1] + self.total_offset[1] + self.cell_offset[1] +
                loc.CRAFT_POS_OFFSET[1] + loc.CRAFT_CELL_IMPERFECTION[1]
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
        :param apply_alpha: accélère l'affichage
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
            if el.get_name() != loc.EMPTY:
                self.blit_cell(screen, (i, self.grid_size[1]), el)

        if self.is_shown:
            screen.blit(self.image, self.image.get_rect(topleft=self.pos))
            screen.blit(self.craft_img, self.craft_img.get_rect(topleft=tuple(self.craft_pos)))

            # ici pour l'inventaire
            for y, line in enumerate(self.objects):
                for x, el in enumerate(line):
                    if loc.EMPTY != el.get_name():
                        self.blit_cell(screen, (x, y), el)

            # ici pour le menu d'assemblage
            for y, line in enumerate(self.crafting_station[0]):
                for x, el in enumerate(line):
                    if loc.EMPTY != el.get_name():
                        self.blit_cell(screen, (x + self.grid_size[0], y), el)
            if loc.EMPTY != self.crafting_station[1][0].get_name():
                self.blit_cell(screen, (self.grid_size[0] + 4, 1), self.crafting_station[1][0])

            # on affiche l'objet déplacé en dernier pour qu'il se retrouve devant
            if (self.is_pressed["bool"] or self.is_pressed["bool_right"]) and not self.is_pressed["crafted"]:
                el = self.is_pressed["cary"]
                pos = pygame.mouse.get_pos()
                screen.blit(el.get_img(), el.get_img().get_rect(center=pos))
                screen.blit(
                    el.get_n_img(),
                    el.get_n_img().get_rect(center=(pos[0] + self.numb_offset[0] / 2, pos[1] + self.numb_offset[1] / 2))
                )
