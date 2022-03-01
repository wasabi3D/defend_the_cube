import GameManagement.Utilities.Objects as Obj
from GameManagement.locals import N, NE, NW, S, SE, SW, E, W, CENTER
import GameManagement.singleton as sing
import GameManagement.SceneManager as Sm
import pygame


class BaseUIObject(Obj.GameObject):
    def __init__(self, pos: pygame.Vector2, rotation: float, object_scale: pygame.Vector2, image: pygame.Surface,
                 components: list, anchor: str = NW):
        super().__init__(pos, rotation, object_scale, image, components)
        self.anchor = anchor
        self.mouse_in_rect = False

    def get_real_pos(self) -> pygame.Vector2:
        pre = super().get_real_pos()
        if self.parent is None:
            x_modif = sing.ROOT.screen_dim[0] / 2
            y_modif = sing.ROOT.screen_dim[1] / 2
            pre += sing.ROOT.cur_scene.main_camera.pos + pygame.Vector2(x_modif, y_modif)
        else:
            x_modif = self.parent.rect.width / 2
            y_modif = self.parent.rect.height / 2

        if self.anchor == CENTER:
            return pre
        elif self.anchor == N:
            return pre + pygame.Vector2(0, -y_modif)
        elif self.anchor == E:
            return pre + pygame.Vector2(x_modif, 0)
        elif self.anchor == S:
            return pre + pygame.Vector2(0, y_modif)
        elif self.anchor == W:
            return pre + pygame.Vector2(-x_modif, 0)
        elif self.anchor == NE:
            return pre + pygame.Vector2(x_modif, -y_modif)
        elif self.anchor == SE:
            return pre + pygame.Vector2(x_modif, y_modif)
        elif self.anchor == SW:
            return pre + pygame.Vector2(-x_modif, y_modif)
        elif self.anchor == NW:
            return pre + pygame.Vector2(-x_modif, -y_modif)

    def get_screen_pos(self) -> pygame.Vector2:
        # return self.get_real_pos() - pygame.Vector2(sing.ROOT.screen_dim[0] / 2, sing.ROOT.screen_dim[1] / 2)
        return self.get_real_pos()

    def blit(self, screen: pygame.Surface, camera_pos_modifier: pygame.Vector2) -> None:
        pos = self.get_real_pos()
        screen.blit(self.alpha_converted(), self.image.get_rect(center=(pos.x, pos.y)))
        for child in self.children.values():
            child.blit(screen, camera_pos_modifier)

    def on_mouse_click_down(self, scene: Sm.Scene, mouse_pos: pygame.Vector2, button: int):
        pass

    def on_mouse_click_up(self, scene: Sm.Scene, mouse_pos: pygame.Vector2, button: int):
        pass

    def on_mouse_rect_enter(self, scene: Sm.Scene, mouse_pos: pygame.Vector2):
        pass

    def on_mouse_rect_exit(self, scene: Sm.Scene, mouse_pos: pygame.Vector2):
        pass





