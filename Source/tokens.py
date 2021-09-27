from pygame import draw, Surface
from sprite_class import sprite

import move_utils as move


class element(sprite):
    def collide(self, collider):
        if move.rect_collision(self, collider):
            return True
        return False

    def generate_surface(self, map=None):
        pass


class tokens_manager():
    def __init__(self):
        self.collectible_dict = {
            "center0" : False,
            "left0" : True }

    def collect(self, id):
        self.collectible_dict[id] = True

    # We use this for now to make it easier lol
    def get(self, id):
        return self.collectible_dict[id]


class yummle(element):
    layer = "TOKEN"

    def __init__(self, pos, size, id):
        self.x = pos[0]
        self.y = pos[1]

        self.w = size[0]
        self.h = size[1]

        self.id = id
        self.tapped = False

        self.c = (155, 35, 155)

    def update_move(self, game):
        if game.TOKEN_MANAGER.get(self.id):
            self.tapped = True

        if self.tapped is True:
            game.TOKEN_MANAGER.collect(self.id)
            self.kill()

    def collide(self, collider):
        if move.rect_collision(self, collider):
            self.tapped = True
            return True

        return False

    def update_draw(self, game):
        rel_x = self.x - game.camera_obj.x
        rel_y = self.y - game.camera_obj.y

        draw.circle(game.win, self.c, (rel_x + self.w/2, rel_y + self.h/2), self.w/2)
