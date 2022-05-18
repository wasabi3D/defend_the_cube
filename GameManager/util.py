from typing import Union, Type, Optional

import pygame
from pygame.math import Vector2
from pygame.sprite import Sprite
import math
from GameManager.funcs import rad2deg, tuple2Vec2, is_included
import GameManager.singleton as sing


class SurfaceModifier:
    """
    Classe qui permet de modifier la luminosité et l'alpha d'un sprite.
    """
    def __init__(self, r, g, b, a):
        """
        Plus les valeurs de r, g, b sont faibles, plus le sprite est sombre.

        :param r: L'intensité de rouge
        :param g: L'intensité de vert
        :param b: L'intensité de bleu
        :param a: L'alpha du sprite
        """
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        self.correction()

    def to_tuple(self) -> tuple[int, int, int, int]:
        """
        Transforme les attributs en forme de tuple.

        :return: (r, g, b, a)
        """
        self.correction()
        return self.r, self.g, self.b, self.a

    def set_rgb(self, value: int) -> None:
        """
        Fonction qui permet de mettre à jour les valeurs de r, g et b.

        :param value: La valeur que l'utilisateur souhaite mettre.
        """
        self.r = self.g = self.b = value

    def add_rgb(self, value: Union[int, float]) -> None:
        """
        Fonction qui permet de ajouter une certaine valeur aux attributs r, g et b.

        :param value: La valeur que l'utilisateur souhaite ajouter.
        """
        self.r += value
        self.g += value
        self.b += value

    def set_alpha(self, value: int) -> None:
        """
        Fonction qui permet de mettre à jour l'alpha.

        :param value: La valeur que l'utilisateur souhaite mettre.
        """
        self.a = value

    def add_alpha(self, value: Union[int, float]) -> None:
        """
        Fonction qui permet de ajouter une certaine valeur à l'alpha.

        :param value: La valeur que l'utilisateur souhaite ajouter.
        """
        self.a += value

    def correction(self) -> None:
        """
        Fonction qui permet de rectifier les valeurs des attributs.
        Les attributs doivent être un int compris entre 0 et 255
        sinon pygame n'accepte pas.
        """
        self.r = int(max(0, min(255, self.r)))
        self.g = int(max(0, min(255, self.g)))
        self.b = int(max(0, min(255, self.b)))
        self.a = int(max(0, min(255, self.a)))


class GameObject(Sprite):
    """
    La base de tous les objets utilisables dans le jeu.
    """

    def __init__(self, pos: Vector2, rotation: float, image: pygame.Surface, name: str, enabled=True,
                 parent=None, alpha=255, tags: Optional[list[str]] = None, simple_mouse_up=False):
        """
        :param pos: La position initiale de l'objet. La valeur par défaut est pygame.Vector2(0, 0).
        :param rotation: La rotation en radian initiale de l'objet. La valeur par défaut est 0.
        :param image: L'image de l'objet initiale.
        :param enabled: Si l'objet est active quand ce dernier est crée ou pas.
        :param name: Le nom de l'objet.
        :param simple_mouse_up: si on détecte le mouse up event même si la souris n'est pas dans l'image
        """

        super().__init__()
        self.pos = pos
        self.rotation = rotation
        self.image: pygame.Surface = image
        self.copy_img: pygame.Surface = self.image.copy()
        self.rect: pygame.Rect = self.image.get_rect(center=(self.pos.x, self.pos.y))
        self.children: ChildrenHolder[str, GameObject] = ChildrenHolder(self)
        self.name: str = name
        self.parent: Union[GameObject, None] = parent
        self.surf_mult: SurfaceModifier = SurfaceModifier(255, 255, 255, alpha)
        self.enabled = enabled
        self.tags = [] if tags is None else tags
        self.simple_mouseup = simple_mouse_up
        self.early_update_done, self.update_done = False, False
        self.last_early_update, self.last_update = 0, 0

        self.mouse_in_rect = False

        self.rotate(rotation, False)

    def blit(self, screen: pygame.Surface, apply_alpha=True) -> None:
        """
        Affiche l'objet sur la fenêtre.

        :param screen: La fenêtre où on affiche l'objet.
        :param apply_alpha: Si on comine l'image avec self.surf_mult(=transparence) ou pas
        :param optional_rect: Le rect qu'on veut utiliser a la place (si il y en a)
        """
        if not self.enabled:
            return
        at = self.get_screen_pos()
        screen.blit(self.alpha_converted() if apply_alpha else self.image,
                    self.image.get_rect(center=(at.x, at.y)))
        for child in self.children.values():
            child.blit(screen, apply_alpha)

    def blit_children(self, screen, apply_alpha=True) -> None:
        """
        Affiche les objets enfants sur la fenêtre.

        :param screen: La fenêtre où on affiche l'objet.
        :param apply_alpha: Si on comine l'image avec self.surf_mult(=transparence) ou pas
        """
        for child in self.children.values():
            child.blit(screen, apply_alpha)

    def translate(self, movement: Vector2, additive=True) -> None:
        """
        Fonction qui permet de modifier la position de l'objet.

        :param movement: Un vecteur qui precise le mouvement(déplacement).
        :param additive: Si True, la fonction additione la valeur du paramère au position actuelle. Sinon elle va
            remplacer la position actuelle par la valeur donnée.
        :return:
        """
        if additive:
            self.pos += movement
        else:
            self.pos = movement
        self.rect = self.image.get_rect(center=(self.pos.x, self.pos.y))

    def rotate(self, rotation: float, additive=True) -> None:
        """
        Fonction qui permet de modifier la rotation de l'objet.

        :param rotation: La rotation en radian.
        :param additive: Si True, la fonction additione la valeur du paramère au rotation actuelle. Sinon elle va
           remplacer la rotation actuelle par la valeur donnée.
        :return:
       """
        if not additive and rotation == self.rotation:
            return
        b4_rct = self.image.get_rect(center=self.rect.center)
        if additive:
            self.rotation += rotation
        else:
            self.rotation = rotation
        self.rotation %= math.pi * 2
        rotated = pygame.transform.rotate(self.copy_img, rad2deg(self.rotation))
        rct = rotated.get_rect(center=b4_rct.center)
        self.image = rotated
        self.rect = rct

        for child in self.children.values():
            child.rotate(rotation, additive)

    def early_update(self) -> None:
        """
        Fonction appellée au début d'une frame, avant les events.
        """
        if sing.ROOT.tick_count != self.last_early_update:
            self.early_update_done = False
        if self.early_update_done:
            return
        if is_included(tuple2Vec2(pygame.mouse.get_pos()), self.image.get_rect(center=self.get_screen_pos())):
            if not self.mouse_in_rect:
                self.on_mouse_rect_enter()
                self.mouse_in_rect = True

            for btn, state in enumerate(sing.ROOT.mouse_downs):
                if state:
                    self.on_mouse_down(btn)

            for btn, state in enumerate(sing.ROOT.mouse_ups):
                if state:
                    self.on_mouse_up(btn)
        else:
            if self.mouse_in_rect:
                self.on_mouse_rect_exit()
                self.mouse_in_rect = False

            if self.simple_mouseup:
                for btn, state in enumerate(sing.ROOT.mouse_ups):
                    if state:
                        self.on_mouse_up(btn)

        self.early_update_done = True
        self.last_early_update = sing.ROOT.tick_count

        for child in self.children.values():
            child.early_update()

    def update(self) -> None:
        """
        Fonction appellée après early_update() et les events.
        Permet de mettre à jour l'objet et de performer certains actions en overload-ant cette fonction.
        """
        if sing.ROOT.tick_count != self.last_update:
            self.update_done = False
        if self.update_done:
            return

        self.last_update = sing.ROOT.tick_count

        for child in self.children.values():
            child.update()

    def get_real_pos(self) -> Vector2:
        """
        Renvoie la position réelle de l'objet sur l'écran. self.pos représente la position relative par rapport au
        parent de l'objet mais cette fonction permet de savoir la position absolue en tenant compte la rotation de
        son parent, position relative, etc...

        :return: self.pos si l'objet n'a pas de parent, sinon sa position absolue.
        """

        if self.parent is None:
            return self.pos.copy()
        else:
            par_pos = self.parent.get_real_pos()
            rel_pos = self.pos + par_pos
            prot = self.parent.rotation

            vec = Vector2(rel_pos.x - par_pos.x, rel_pos.y - par_pos.y)
            vec.rotate_rad_ip(-prot)
            return par_pos + vec

    def get_screen_pos(self) -> Vector2:
        """
        Renvoie la position qu'on voit sur l'écran. (0, 0) est le coin en haut à gauche de l'écran.

        :return: La position.
        """
        rp = self.get_real_pos()
        return rp + tuple2Vec2(sing.ROOT.screen_dim) / 2 - sing.ROOT.camera_pos

    def alpha_converted(self) -> pygame.Surface:
        """
        Permet de générer l'image combiné avec self.surf_mult

        :return: L'image avec transparence.
        """
        tmp = self.image.copy()
        tmp.fill(self.surf_mult.to_tuple(), None, pygame.BLEND_RGBA_MULT)
        return tmp

    def on_mouse_down(self, button: int):
        pass

    def on_mouse_up(self, button: int):
        pass

    def on_mouse_rect_enter(self):
        pass

    def on_mouse_rect_exit(self):
        pass

    def get_collision_rect(self) -> pygame.Rect:
        return self.image.get_rect(center=self.get_real_pos())

    def set_enabled(self, state: bool) -> None:
        self.enabled = state


class ChildrenHolder(dict):
    """
    Une classe qui permet de contenir les objets enfants d'un gameobject. Tous gameobjets ont au moins 1 instance de
    ChildrenHolder.
    Hérite dict pour faciliter l'accès aux objets.
    """

    def __init__(self, parent: GameObject):
        """

        :param parent: Le parent objet qui possède cette instance.
        """
        super().__init__()
        # self.children: dict[str, GameObject] = {}
        self.parent: GameObject = parent

    def add_gameobject(self, obj: GameObject) -> None:
        """
        Permet de ajouter un gameobject à un gameobject en tant que objet enfant.

        :param obj: L'objet qu'on veut ajouter.
        :return:
        """
        obj.parent = self.parent
        self.setdefault(obj.name, obj)

    def add_gameobjects(self, *objects: GameObject) -> None:
        """
        Permet de ajouter des gameobjects à un gameobject en tant que objet enfant.

        :param objects: Les objets qu'on veut ajouter.
        :return:
        """
        for obj in objects:
            self.add_gameobject(obj)

    def get_child_by_name(self, name: str) -> Union[GameObject, None]:
        """
        Retourne l'objet qui possède le nom donné.
        Alias de ChildrenHolder()[name]

        :param name: Nom de l'objet que l'utilisateur cherche.
        :return: L'objet si il existe dans le dict sinon None.
        """
        if name in self.keys:
            return self[name]
        else:
            return None
