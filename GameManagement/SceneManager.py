import pygame

import GameManagement.Utilities


class Scene:
    def __init__(self):
        self.gameObjects: list[GameManagement.Utilities.GameObject] = []

    def start(self):
        for g in self.gameObjects:
            g.start()

    def start_of_frame(self):
        for g in self.gameObjects:
            g.early_update()

    def update(self):
        for g in self.gameObjects:
            g.update()

    def blit_objects(self, screen: pygame.Surface):  # THIS IS JUST A TEST
        for g in self.gameObjects:
            g.blit(screen)
    
