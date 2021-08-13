from pygame import draw, Surface
from sprite_class import sprite

import move_utils as move
import draw_utils as drawu

from colour_manager import colours

import random
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

        self.startpos = (self.x, self.y)

        print(*self.startpos)

        self.c = (155, 35, 155)

    def update_move(self, game): # wtf is assert # raise error if the cond is not true # right
        # print(f"{self.x} {self.startpos[0]}")
        assert self.x == self.startpos[0] and self.y == self.startpos[1]

        if self.x == 1960:
            print(self.x)

    def update_draw(self, game):
        rel_x = self.x - game.camera_obj.x
        rel_y = self.y - game.camera_obj.y

        # for s in game.sprites["CAMERACOLLIDER"]:
        #     if s.x == 1960:
        #         assert self is not s

        assert self.x == self.startpos[0] and self.y == self.startpos[1]

        # print(self.x, self) # does this work
        print(self.startpos[0], self) # does this work

        # lemme check

        # testing on one i know is wrong
        # if self.x > 1080:
            # print(f"X: {rel_x} Y: {rel_y}")
            # print(f"aX: {self.x} aY: {self.y}")
            # the one we are looking for has like an x of width - 60

        draw.rect(game.win, self.c, (rel_x, rel_y, self.w, self.h))

    def collide(self, collider):
        if move.rect_collision(self, collider):
            return True
        return False


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

        if self.active:
            img = asset.SPRITE.checkpoint_true
        else:
            img = asset.SPRITE.checkpoint_false

        game.win.blit(img, (rel_x, rel_y))


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

    def update_draw(self, game):
        rel_x = self.x - game.camera_obj.x
        rel_y = self.y - game.camera_obj.y

        # draw.rect(game.win, self.c, (rel_x, rel_y, self.w, self.h))

        game.win.blit(self.surface, (rel_x, rel_y))


class hazard(element):
    layer = "HAZARD"

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
            # print(f"we got {collider}")

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


class level_transition(element):
    layer = "LEVELTRANSITION"
    persistent = True

    def __init__(self, pos, size, target_level, spawnkey):
        self.x = pos[0]
        self.y = pos[1]

        self.w = size[0]
        self.h = size[1]

        # Whether or not the level_transition is going to be interracted with on the x or y is decided by it's width vs height
        # GoodCodeTM
        if self.w > self.h:
            self.vertical = True
        else:
            self.vertical = False

        self.c = (35, 35, 155)

        self.target = target_level
        self.k = spawnkey

    def update_draw(self, game):
        self.game = game
        rel_x = self.x - game.camera_obj.x
        rel_y = self.y - game.camera_obj.y

        draw.rect(game.win, self.c, (rel_x, rel_y, self.w, self.h))

    def collide(self, collider):
        if self.destroying:
            return

        if collider.layer == "PLAYER":
            cc = (collider.x + collider.w/2, collider.y + collider.h/2, 1, 1)

            if self.x + self.w > cc[0] and self.x < cc[0] + cc[2]:
                if self.y + self.h > cc[1] and self.y < cc[1] + cc[3]:

                    # Decide direction of the screen transition
                    if self.vertical is True:
                        if collider.y_speed > 0:
                            direction = "DOWN"
                        else:
                            direction = "UP"
                    else:
                        if collider.PHYS.left:
                            direction = "RIGHT"
                        elif collider.PHYS.right:
                            direction = "LEFT"

                    # self.levelwipe = drawu.screenwipe(direction, asset.TEXTURE.screenwipe, 40, (155, 35, 35), self.game)
                    self.levelwipe = drawu.bubblewipe(direction=direction, num_bubbles=9, tick=1, colour=collider.c, randspeed=True, randcol=True, game=self.game)
                    self.game.add_sprite(self.levelwipe)
                    collider.PHYS.freeze = True
                    self.destroying = True

        else:
            if move.rect_collision(self, collider):
                return True

        return False

    def update_destroy(self, game):
        if self.levelwipe.blocking:
            self.game.load_level(self.target)
            spawnpos = self.game.spawnkeys[self.k]
            p = game.sprites["PLAYER"][0]

            p.PHYS.freeze = False
            p.set_spawn(spawnpos)
            print(spawnpos)
            p.respawn(halt=True)


class spawn_key(element):
    def __init__(self, pos, key):
        self.x = pos[0]
        self.y = pos[1]
        self.k = key
