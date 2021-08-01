from pygame import draw, Surface
from sprite_class import sprite

import move_utils as move

import asset


class element(sprite):
    def collide(self, collider):
        if move.rect_collision(self, collider):
            return True
        return False


class camera_collider(element):
    layer = "CAMERACOLLIDER"

    def __init__(self, pos, size):
        self.x = pos[0]
        self.y = pos[1]

        self.w = size[0]
        self.h = size[1]


class checkpoint(element):
    layer = "CHECKPOINTS"

    def __init__(self, pos, size):

        self.x = pos[0]
        self.y = pos[1]

        self.w = size[0]
        self.h = size[1]

        self.c = (255, 160, 20)
        self.active_c = (35, 200, 35)

        self.active = False

    def update_move(self, game):
        p_x, p_y = game.sprites["PLAYER"][0].spawnpos

        # print(f"x: {self.x} px: {p_x}  y: {self.y}  py: {p_y}")

        if self.x == p_x and self.y == p_y:
            self.active = True
        else:
            self.active = False

    def update_draw(self, game):
        rel_x = self.x - game.camera_obj.x
        rel_y = self.y - game.camera_obj.y

        c = self.c
        if self.active:
            c = self.active_c

        draw.rect(game.win, c, (rel_x, rel_y, self.w, self.h))


class platform(element):
    layer = "TERRAIN"

    def __init__(self, pos, size):
        self.x = pos[0]
        self.y = pos[1]

        self.w = size[0]
        self.h = size[1]

        self.c = (35, 35, 155)

        self.surface = Surface((self.w, self.h))
        for y in range(0, self.h, 20):
            for x in range(0, self.w, 20):
                self.surface.blit(asset.TEXTURE.platform(), (x, y))

    def update_move(self, game):
        pass

    def update_draw(self, game):
        rel_x = self.x - game.camera_obj.x
        rel_y = self.y - game.camera_obj.y

        # draw.rect(game.win, self.c, (rel_x, rel_y, self.w, self.h))

        game.win.blit(self.surface, (rel_x, rel_y))


class hazard(element):
    layer = "TERRAIN"

    def __init__(self, pos, size):

        self.x = pos[0]
        self.y = pos[1]

        self.w = size[0]
        self.h = size[1]

        self.c = (35, 35, 155)

        def dead_tv_channel():
            surf = Surface((self.w, self.h))
            for y in range(0, self.h, 20):
                for x in range(0, self.w, 20):
                    surf.blit(asset.TEXTURE.hazard(), (x, y))

            return surf

        self.tv_static = [dead_tv_channel() for i in range(10)]
        self.iter = 0
        self.surface = Surface((self.w, self.h))

    def collide(self, collider):
        if move.rect_collision(self, collider):
            collider.destroying = True

    def update_move(self, game):
        self.surface.blit(self.tv_static[self.iter], (0, 0))
        self.iter += 1
        if self.iter == len(self.tv_static):
            self.iter = 0

    def update_draw(self, game):
        rel_x = self.x - game.camera_obj.x
        rel_y = self.y - game.camera_obj.y

        # draw.rect(game.win, self.c, (rel_x, rel_y, self.w, self.h))

        game.win.blit(self.surface, (rel_x, rel_y))
