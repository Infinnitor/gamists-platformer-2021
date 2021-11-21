from pygame import draw, Surface
from sprite_class import sprite
from tokens import *

import move_utils as move
import math

import draw_utils as drawu
from colour_manager import colours

import bracket_match as bracket
import asset


class element(sprite):
    def collide(self, collider):
        if move.rect_collision(self, collider):
            return True
        return False

    def generate_surface(self, map=None):
        pass


class background(element):
    layer = "BACKGROUND"
    persistent = True

    leveltheme = "MAIN"

    def __init__(self, pos, size):
        self.x = pos[0]
        self.y = pos[1]

        self.w = size[0]
        self.h = size[1]

        self.surface = Surface((self.w, self.h))

    def generate_surface(self, map=None):
        self.texture = asset.TEXTURE._blank

        if self.leveltheme == "APEOUT":
            self.texture = asset.TEXTURE.bg_texture
        elif self.leveltheme == "MAIN":
            self.texture = asset.TEXTURE.bg_texture

        pbg_x, pbg_y = self.texture.get_size()

        # Made a surface the size of the entire level, with a repeated texture on it
        for y in range(0, (self.h // pbg_y) * pbg_y + pbg_y, pbg_y):
            for x in range(0, (self.w // pbg_x) * pbg_x + pbg_x, pbg_x):
                self.surface.blit(self.texture, (x, y))

    def update_draw(self, game):
        rel_x = self.x - game.camera_obj.x
        rel_y = self.y - game.camera_obj.y

        # game.win.blit(self.surface, (rel_x, rel_y))
        draw.rect(game.win, (25, 75, 25), (0, 0, game.win_w, game.win_h))


class camera_collider(element):
    layer = "CAMERACOLLIDER"
    persistent = True

    def __init__(self, pos, size):
        self.x = pos[0]
        self.y = pos[1]

        self.w = size[0]
        self.h = size[1]

        self.c = (155, 35, 155)

    def update_draw(self, game):
        rel_x = self.x - game.camera_obj.x
        rel_y = self.y - game.camera_obj.y

        draw.rect(game.win, self.c, (rel_x, rel_y, self.w, self.h))

    def collide(self, collider):
        if collider.layer == "PLAYER":
            if self.x + self.w > collider.x + collider.w and self.x < collider.x:
                if self.y + self.h > collider.y + collider.h and self.y < collider.y:
                    collider.destroying = True
                    return None

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
        p_x, p_y = game.PLAYER.spawnpos

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
    leveltheme = "MAIN"

    def __init__(self, pos, size):
        self.x = pos[0]
        self.y = pos[1]

        self.w = size[0]
        self.h = size[1]

        self.c = colours.blue

    def generate_surface(self, map=None):
        self.surface = Surface((self.w, self.h))

        self.texture = asset.TEXTURE._blank
        if self.leveltheme == "BEAN":
            self.texture = asset.TEXTURE.bean_texture()
        elif self.leveltheme == "MAIN":
            self.texture = asset.TEXTURE.bean_texture()

        if map is None:
            for y in range(0, self.h, 20):
                for x in range(0, self.w, 20):

                    self.surface.blit(self.texture, (x, y))

        # If there is an active platform map
        else:
            self.surface.blit(map, (0, 0), (self.x, self.y, self.w, self.h))

    def update_draw(self, game):
        rel_x = self.x - game.camera_obj.x
        rel_y = self.y - game.camera_obj.y

        # game.win.blit(self.surface, (rel_x, rel_y))
        draw.rect(game.win, (10, 10, 10), (rel_x, rel_y, self.w, self.h))


class hazard(element):
    layer = "HAZARD"

    def __init__(self, pos, size):

        self.x = pos[0]
        self.y = pos[1]

        self.w = size[0]
        self.h = size[1]

        self.c = (35, 35, 155)

    def generate_surface(self, map=None):

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

    def update_draw(self, game):
        self.surface.fill(colours.colourkey)
        self.surface.set_colorkey(colours.colourkey)

        self.surface.blit(self.tv_static[self.iter], (0, 0))
        self.iter += 1
        if self.iter == len(self.tv_static):
            self.iter = 0

        rel_x = self.x - game.camera_obj.x
        rel_y = self.y - game.camera_obj.y

        game.win.blit(self.surface, (rel_x, rel_y))


class pogo_point(hazard):
    layer = "POGO"

    def generate_surface(self, map=None):

        stencil = Surface((self.w, self.h))
        stencil.fill(colours.purple)

        draw.circle(stencil, colours.colourkey, (self.w/2, self.h/2), self.w/2)
        stencil.set_colorkey(colours.colourkey)

        def dead_tv_channel():
            surf = Surface((self.w, self.h))
            for y in range(0, self.h, 20):
                for x in range(0, self.w, 20):
                    surf.blit(asset.TEXTURE.hazard(), (x, y))

            surf.blit(stencil, (0, 0))
            surf.set_colorkey(colours.purple)
            return surf

        self.tv_static = [dead_tv_channel() for i in range(10)]
        self.iter = 0
        self.surface = Surface((self.w, self.h))


class moving_hazard(hazard):
    layer = "HAZARD"

    @staticmethod
    def p_array(s):
        return bracket.read_brackets(s, split_on="'", chars=("[", "]"), t=int)

    def __init__(self, start_pos, size, positions, speed):
        self.x = start_pos[0]
        self.y = start_pos[1]

        self.w = size[0]
        self.h = size[1]

        self.c = (35, 35, 155)

        self.positions = []
        for p in positions.split(","):
            r = self.p_array(p)
            self.positions.append(r)

        self.m_iter = 0

        self.speed = float(speed)

        self.moving = False

        self.a = 0
        self.xmove = 0
        self.ymove = 0

    def angle_calc(self):
        x_d = self.positions[self.m_iter][0] - self.x
        y_d = self.positions[self.m_iter][1] - self.y

        self.a = math.atan2(y_d, x_d)

        self.xmove = math.cos(self.a)
        self.ymove = math.sin(self.a)

    def update_move(self, game):
        if self.moving is False:
            self.m_iter += 1
            if self.m_iter == len(self.positions):
                self.m_iter = 0

            self.angle_calc()
            self.moving = True

        self.x += self.xmove * self.speed
        self.y += self.ymove * self.speed

        if math.dist((self.x, self.y), self.positions[self.m_iter]) < 2:
            self.moving = False


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
        rel_x = self.x - game.camera_obj.x
        rel_y = self.y - game.camera_obj.y

        draw.rect(game.win, self.c, (rel_x, rel_y, self.w, self.h))

    def collide(self, collider, game):
        if self.destroying:
            return

        if collider.layer == "PLAYER":
            cc = (collider.x + collider.w/2, collider.y + collider.h/2, 1, 1)

            if self.x + self.w > cc[0] and self.x < cc[0] + cc[2]:
                if self.y + self.h > cc[1] and self.y < cc[1] + cc[3]:

                    # Decide direction of the screen transition
                    if self.vertical is True:
                        if collider.y_speed > 0:
                            direction = "UP"
                        else:
                            direction = "DOWN"
                    else:
                        if collider.PHYS.left:
                            direction = "RIGHT"
                        elif collider.PHYS.right:
                            direction = "LEFT"

                    # self.levelwipe = drawu.screenwipe(direction, asset.TEXTURE.screenwipe, 40, (155, 35, 35), self.game)
                    self.levelwipe = drawu.bubblewipe(direction=direction, num_bubbles=9, tick=1, colour=(35, 110, 125), randspeed=True, randcol=True, game=game)
                    game.add_sprite(self.levelwipe)
                    collider.PHYS.freeze = True
                    self.destroying = True

        else:
            if move.rect_collision(self, collider):
                return True

        return False

    def update_destroy(self, game):
        if self.levelwipe.blocking:
            game.load_level(self.target)
            spawnpos = game.spawnkeys[self.k]

            game.PLAYER.PHYS.freeze = False
            game.PLAYER.set_spawn(spawnpos)
            game.PLAYER.respawn(halt=True)
