import pygame

from GameManagement.Utilities import Objects
from GameManagement.Utilities.Components import CameraComponent

from typing import Union


class Scene:
    def __init__(self):
        self.gameObjects: dict[str, Objects.GameObject] = {}
        self.main_camera: Union[Objects.GameObject, None] = None

    def start(self):
        for g in self.gameObjects.values():
            g.start(self)
        if self.main_camera is not None:
            self.main_camera.start(self)

    def start_of_frame(self):
        for g in self.gameObjects.values():
            g.early_update(self)
        if self.main_camera is not None:
            self.main_camera.early_update(self)

    def update(self):
        for g in self.gameObjects.values():
            g.normal_update(self)
        if self.main_camera is not None:
            self.main_camera.normal_update(self)

    def blit_objects(self, screen: pygame.Surface):
        if self.main_camera is None:
            return
        cm: CameraComponent = self.main_camera.get_component(CameraComponent)
        cm.blit_objects(self.main_camera, self, screen)

    def add_gameobject(self, obj: Objects.GameObject, name="") -> None:
        self.gameObjects.setdefault(obj.name if name == "" else name, obj)

    def register_main_camera(self, obj: Objects.GameObject) -> bool:
        if obj.has_component(CameraComponent):
            self.main_camera = obj
            return True
        else:
            return False


    
