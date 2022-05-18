import pygame
import sys
import GameManager.singleton as sing
import GameManager.util as util
import re
from typing import Optional
from collections import OrderedDict


class GameRoot:
    """

    La classe pour la géstion du jeu entière
    """
    def __init__(self, screen_dimension: tuple[int, int], default_background_color: tuple[int, int, int], title: str,
                 resources_root_path: str, camera_pos: pygame.Vector2, fps_limit=60, display_flag=pygame.SCALED):
        """

        :param screen_dimension: La dimension de la fenêtre
        :param default_background_color: La couleur du fond
        :param title: Le titre
        :param resources_root_path: La base du path pour tous les ressources(images, polices...)
        :param camera_pos: La position de la caméra
        :param fps_limit: La limite de l'fps
        :param display_flag: Option pour la fenêtre du pygame
        """
        pygame.init()
        sing.ROOT = self
        self.display: pygame.Surface = pygame.display.set_mode(screen_dimension, flags=display_flag)
        pygame.display.set_caption(title)
        self.background: tuple[int, int, int] = default_background_color
        self.fps_limit = fps_limit
        self.clock = pygame.time.Clock()
        self.delta = 0
        self.screen_dim = screen_dimension
        self.resources_path = resources_root_path
        self.key_ups = []
        self.key_downs = []
        self.mouse_ups: list[bool, bool, bool] = [False, False, False]
        self.mouse_downs: list[bool, bool, bool] = [False, False, False]
        self.camera_pos: pygame.Vector2 = camera_pos
        self.game_objects: OrderedDict[str, util.GameObject] = OrderedDict()
        self.collidable_objects: list[util.GameObject] = []
        self.global_fonts: dict[str, pygame.font.Font] = {}
        self.object_collision_rects: list[pygame.Rect] = []
        self.objects2be_removed: list[util.GameObject] = []
        self.objects2be_added: list[util.GameObject] = []
        self.objects_by_tag: dict[str, list[util.GameObject]] = {}
        self.new_object_index = 0
        self.display_priority: list[str] = []
        self.parameters: dict = {}
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.tick_count = 0

    def mainloop(self):
        """
        Fonction pour lancer le jeu
        """

        self.delta = 0
        while True:
            self.object_collision_rects.clear()
            for l in self.objects_by_tag.values():
                l.clear()
            t = pygame.time.get_ticks()
            self.key_ups.clear()
            self.key_downs.clear()
            last_mouse_ups = self.mouse_ups.copy()
            last_mouse_downs = self.mouse_downs.copy()
            self.mouse_ups.clear()
            self.mouse_downs.clear()
            self.mouse_ups = [False, False, False]
            self.mouse_downs = [False, False, False]

            # _____EVENTS_____
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                elif event.type == pygame.KEYDOWN:
                    self.key_downs.append(event.key)
                elif event.type == pygame.KEYUP:
                    self.key_ups.append(event.key)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button > 3:  # MOUSE SCROLL
                        continue
                    # if not last_mouse_ups[event.button - 1]:
                    self.mouse_ups[event.button - 1] = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button > 3:  # MOUSE SCROLL
                        continue
                    # if not last_mouse_downs[event.button - 1]:
                    self.mouse_downs[event.button - 1] = True

            # ___________

            # ___MAIN UPDATE___
            try:
                for gm in self.game_objects.values():
                    if gm.enabled:
                        gm.early_update()
            except RuntimeError:
                pass

            try:
                for gm in self.game_objects.values():
                    if gm.enabled:
                        gm.update()
            except RuntimeError:
                pass
            # _________________

            # ___ ADD/REMOVE OBJECTS ___
            for gm in self.objects2be_added:
                self.game_objects.setdefault(gm.name, gm)

            for gm in self.objects2be_removed:
                try:
                    self.game_objects.pop(gm.name)
                except KeyError:
                    pass
                self.remove_collidable_object(gm)
            self.objects2be_added.clear()
            self.objects2be_removed.clear()
            # _________________

            # __ BLIT THINGS ON THE SCREEN __
            self.display.fill(self.background)
            for gm in self.game_objects:
                if self.game_objects[gm].enabled and gm not in self.display_priority:
                    self.game_objects[gm].blit(self.display)
            for gm in reversed(self.display_priority):
                if gm in self.game_objects:
                    if self.game_objects[gm].enabled:
                        self.game_objects[gm].blit(self.display)
            pygame.display.update()
            self.clock.tick(self.fps_limit)
            self.delta = (pygame.time.get_ticks() - t) / 1000
            self.tick_count += 1

    def add_gameObject(self, *gameObject: util.GameObject, immediate=False):
        """
        Fonction pour ajouter un objet

        :param immediate: Si on l'ajoute immediatement
        :param gameObject: L'objet qu'on veut ajouter
        """
        if not immediate:
            self.objects2be_added += list(gameObject)
        else:
            for g in gameObject:
                self.game_objects.setdefault(g.name, g)
        return self

    def add_collidable_object(self, gameObject: util.GameObject) -> None:
        """
        Fonction pour ajouter un objet qui possède un hitbox

        :param gameObject: L'objet qu'on veut ajouter
        """
        self.collidable_objects.append(gameObject)

    def calculate_collision_rects(self) -> None:
        """
        Calcule les hitboxes pour tous les objets

        """
        if len(self.object_collision_rects) == 0:
            self.object_collision_rects = list(map(lambda obj: obj.get_collision_rect(), self.collidable_objects))

    def is_colliding(self, rect: pygame.Rect, exclude: Optional[str] = None) -> int:
        """
        Fonction pour vérifier si le rect donné est en contact avec un autre objet

        :param rect: Le rect qu'on veut vérifier
        :param exclude: Exception pour pas détecter une collision avec
        :return: L'index de l'objet si il est en contact sinon -1
        """
        self.calculate_collision_rects()
        il = rect.collidelistall(self.object_collision_rects)
        for i in il:
            if i > len(self.collidable_objects) - 1:
                continue
            if exclude is None or not re.match(exclude, self.collidable_objects[i].name):
                return i
        return -1

    def collide_all(self, rect: pygame.Rect, exclude: Optional[str] = None) -> tuple[int]:
        """
        Pareil que is_colliding mais peut détecter plusieurs objets

        :param rect: Le rect qu'on veut vérifier
        :param exclude: Exceptions pour pas détecter une collision avec
        :return: Les indexes des objets si le rect est en contact sinon un tuple vide
        """
        self.calculate_collision_rects()
        il = rect.collidelistall(self.object_collision_rects)
        ret = []
        for i in il:
            if i > len(self.collidable_objects) - 1:
                continue
            if exclude is None or not re.match(exclude, self.collidable_objects[i].name):
                ret.append(i)
        return tuple(ret)

    def remove_collidable_object(self, obj: util.GameObject) -> bool:
        """
        Supprime un objet possédant un hitbox

        :param obj: L'objet qu'on veut supprimer
        :return: True si il réussit sinon False
        """
        for i, o in enumerate(self.collidable_objects):
            if o == obj:
                self.collidable_objects.pop(i)
                return True
        return False

    def remove_object(self, obj: util.GameObject):
        """
        Supprime un objet

        :param obj: L'objet qu'on veut supprimer
        """
        self.objects2be_removed.append(obj)

    def clear_objects(self):
        """
        Supprime tous les objets du jeu
        """
        self.game_objects.clear()
        self.collidable_objects.clear()
        self.object_collision_rects.clear()
        self.objects2be_removed.clear()
        self.objects2be_added.clear()
        self.objects_by_tag.clear()

    def get_obj_list_by_tag(self, tag: str) -> list[util.GameObject]:
        """
        Fonction pour obtenir une liste des objets qui possèdent un tag donné

        :param tag: Le tag
        :return: La liste des objets
        """
        if tag not in self.objects_by_tag.keys():
            self.objects_by_tag[tag] = []

        if len(self.objects_by_tag[tag]) == 0:
            for gm in self.game_objects.values():
                if tag in gm.tags:
                    self.objects_by_tag[tag].append(gm)

        return self.objects_by_tag[tag]

    def setup_priority(self, order: list[str]) -> None:
        self.display_priority = [x for x in order if x in self.game_objects]

    def set_parameter(self, key, value) -> None:
        self.parameters[key] = value

    def modify_volume(self, vol: float) -> None:
        for sound in self.sounds.values():
            sound.set_volume(vol)
