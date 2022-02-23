import pygame
from typing import Union
from pygame.math import Vector2
from pygame.sprite import Sprite
import math
from GameManagement.Utilities.funcs import rad2deg


class BaseObject:
    """
    Définit la base de tous les objets du jeu(camera inclu).
    """
    def __init__(self, pos: Vector2, rotation: float, object_scale: Vector2):
        """

        :param pos: La position initiale de l'objet. La valeur par défaut est pygame.Vector2(0, 0).
        :param rotation: La rotation en radian initiale de l'objet. La valeur par défaut est 0.
        :param object_scale: L'échelle initiale de l'objet. La valeur par défaut est pygame.Vector2(1, 1).
        """
        self.pos: Vector2 = pos  # Position du centre de l'image et non topleft
        self.rotation = rotation
        self.scale = object_scale

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

    def rotate(self, rotation: float, additive=True) -> None:
        """
        Fonction qui permet de modifier la rotation de l'objet.

        :param rotation: La rotation en radian.
        :param additive: Si True, la fonction additione la valeur du paramère au rotation actuelle. Sinon elle va
            remplacer la rotation actuelle par la valeur donnée.
        :return:
        """
        if additive:
            self.rotation += rotation
        else:
            self.rotation = rotation
        self.rotation %= math.pi * 2

    def mscale(self, multiplier: Union[float, int]) -> None:
        """
        Fonction qui permet de modifier l'échelle de l'objet.

        :param multiplier: Multiplicateur de l'échelle.
        :return:
        """
        self.scale *= multiplier

    def scale_to(self, target_scale: Vector2) -> None:
        """
        Fonction qui permet de modifier l'échelle de l'objet.

        :param target_scale: Nouvelle échelle.
        :return:
        """
        self.scale = target_scale


class GameObject(BaseObject, Sprite):
    """
    La base de tous les objets utilisables dans le jeu.
    """
    def __init__(self, pos: Vector2, rotation: float, object_scale: Vector2, image: pygame.Surface, enabled=True,
                 name="", parent=None):
        """

        :param pos: La position initiale de l'objet. La valeur par défaut est pygame.Vector2(0, 0).
        :param rotation: La rotation en radian initiale de l'objet. La valeur par défaut est 0.
        :param object_scale: L'échelle initiale de l'objet. La valeur par défaut est pygame.Vector2(1, 1).
        :param image: L'image de l'objet initiale.
        :param enabled: Si l'objet est active quand ce dernier est crée ou pas.
        :param name: Le nom de l'objet.
        """
        super().__init__(pos, rotation, object_scale)
        self.image = image
        self.copy_img = self.image.copy()
        self.rect = self.image.get_rect(center=(self.pos.x, self.pos.y))
        self.children: ChildrenHolder = ChildrenHolder(self)
        self.components = None
        self.enabled = enabled
        self.name = name
        self.parent: Union[GameObject, None] = parent

    def blit(self, screen: pygame.Surface) -> None:
        """
        Affiche l'objet sur la fenêtre.
        :param screen: La fenêtre où on affiche l'objet.
        :return:
        """
        if self.parent is None:
            screen.blit(self.image, self.rect)
        else:
            at = self.get_real_pos()
            screen.blit(self.image, self.image.get_rect(center=(at.x, at.y)))
        for child in self.children.values():
            child.blit(screen)

    def translate(self, movement: Vector2, additive=True) -> None:
        """
        Fonction qui permet de modifier la position de l'objet.

        :param movement: Un vecteur qui precise le mouvement(déplacement).
        :param additive: Si True, la fonction additione la valeur du paramère au position actuelle. Sinon elle va
            remplacer la position actuelle par la valeur donnée.
        :return:
        """
        super().translate(movement, additive)
        self.rect = self.image.get_rect(center=(self.pos.x, self.pos.y))

    def rotate(self, rotation: float, additive=True) -> None:
        """
        Fonction qui permet de modifier la rotation de l'objet.

        :param rotation: La rotation en radian.
        :param additive: Si True, la fonction additione la valeur du paramère au rotation actuelle. Sinon elle va
           remplacer la rotation actuelle par la valeur donnée.
        :return:
       """
        b4_rct = self.image.get_rect(center=self.rect.center)
        super().rotate(rotation, additive)
        rotated = pygame.transform.rotate(self.copy_img, rad2deg(self.rotation))
        rct = rotated.get_rect(center=b4_rct.center)
        self.image = rotated
        self.rect = rct

        for child in self.children.values():
            child.rotate(rotation, additive)

    def mscale(self, multiplier: Union[float, int]) -> None:
        pass

    def scale_to(self, target_scale: Vector2) -> None:
        super().scale_to(target_scale)
        pygame.transform.scale(self.image, (target_scale.x, target_scale.y), self.image)

    def start(self) -> None:
        """
        Fonction appellée avant l'execution de la première frame d'une scène.
        :return:
        """
        for child in self.children.values():
            child.start()

    def early_update(self) -> None:
        """
        Fonction appellée au début d'une frame, avant les events.
        :return:
        """
        for child in self.children.values():
            child.early_update()

    def update(self) -> None:
        """
        Fonction appellée après early_update() et les events.
        :return:
        """
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
            return self.pos
        else:
            rel_pos = self.pos + self.parent.get_real_pos()
            par_pos = self.parent.get_real_pos()
            prot = self.parent.rotation

            vec = Vector2(rel_pos.x - par_pos.x, rel_pos.y - par_pos.y)
            vec.rotate_rad_ip(-prot)
            return par_pos + vec


class ChildrenHolder(dict):
    """
    Une classe qui permet de contenir les objets enfants d'un gameobject. Tous gameobjets ont au moins 1 instance de
    ChildrenHolder.
    Hérite la classe dict(dictionnaire) pour faciliter l'accès aux objets.
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
