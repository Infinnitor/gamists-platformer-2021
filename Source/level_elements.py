from pygame import draw, Surface
from sprite_class import sprite


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

    def update_draw(self, game):
        rel_x = self.x - game.camera_obj.x
        rel_y = self.y - game.camera_obj.y

        draw.rect(game.win, self.c, (rel_x, rel_y, self.w, self.h))
