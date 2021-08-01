from pygame import draw, Surface
from sprite_class import sprite

import random

import move_utils as move

import asset


class camera_collider(sprite):
    layer = "CAMERACOLLIDER"

    def __init__(self, pos, size):
        self.x = pos[0]
        self.y = pos[1]

        self.w = size[0]
        self.h = size[1]


class checkpoint(sprite):
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


class platform(sprite):
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
                self.surface.blit(asset.JERMA[0], (x, y))

    def add_class_attr(self, game):
        self.tick = move.frametick(7, game)
        self.iter = 0

    def update_move(self, game):
        if self.tick.get():
            self.iter += 1
            if self.iter > 5:
                self.iter = 0
            for y in range(0, self.h, 20):
                for x in range(0, self.w, 20):
                    self.surface.blit(asset.JERMA[self.iter], (x, y))

    def update_draw(self, game):
        rel_x = self.x - game.camera_obj.x
        rel_y = self.y - game.camera_obj.y

        # draw.rect(game.win, self.c, (rel_x, rel_y, self.w, self.h))

        game.win.blit(self.surface, (rel_x, rel_y))
