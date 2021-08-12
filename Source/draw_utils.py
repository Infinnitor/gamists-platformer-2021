import random
from pygame import draw, Surface
from sprite_class import sprite

from colour_manager import colours

import move_utils as move
import asset


class rgb():

    def invert(c, min=0, max=255):

        col = max - c
        if col < min:
            col = min
        return col

    def compliment(colour):
        return tuple([rgb.invert(c) for c in colour])

    def fix(colour, min=0, max=255):
        assert min > -1 and max < 256, "Min and Max must be between 0 and 255"

        fixed_colour = []
        for c in colour:
            if c > max:
                c = max
            elif c < min:
                c = min

            fixed_colour.append(c)

        return tuple(fixed_colour)

    def randomize(colour, lower=-20, upper=20):
        final_colour = [c + random.randint(lower, upper) for c in colour]
        return rgb.fix(final_colour)

    def lerp(c1, c2, point):
        dist_rgb = [c2[i] - c1[i] for i in range(3)]

        return tuple([c1[i] + (dist_rgb[i] * (point / 100)) for i in range(3)])

    class lerp_obj():
        def __init__(self, c1, c2, step=1, kill=True):
            self.c1 = c1
            self.c2 = c2

            self.iter = 0
            self.step = step

            self.kill = kill

        def get(self):
            self.iter += self.step

            if self.iter <= 100:
                return rgb.lerp(self.c1, self.c2, self.iter)
            else:
                if self.kill:
                    return None

                self.iter = 0
                c1 = self.c1
                c2 = self.c2

                self.c1 = c2
                self.c2 = c1

            return rgb.lerp(self.c1, self.c2, self.iter)


class bubblewipe(sprite):
    layer = "FOREGROUND"
    persistent = True

    class bubble(sprite):
        # Layer is just there because it's a sprite ig lol
        layer = "FOREGROUND"

        def __init__(b, pos, max_r, speed, colour):
            b.x = pos[0]
            b.y = pos[1]

            b.r = 0
            b.max_r = max_r

            b.max_size = False
            b.reverse_bool = False
            b.speed = speed

            b.c = (155, 35, 35)

        def reverse(self):
            self.reverse_bool = True

        def update_move(b, game):

            if b.reverse_bool is False:
                b.r += b.speed
                if b.r > b.max_r:
                    b.r = b.max_r
                    b.max_size = True
            else:
                b.r -= b.speed
                if b.r < 0:
                    b.kill()

        def update_draw(b, surface=None):
            assert surface is not None, "You forgot to pass in the correct surface dummy"
            draw.circle(surface, b.c, (b.x, b.y), b.r)

    def __init__(self, direction, num_bubbles, tick, colour, game):
        # LEFT, RIGHT, UP, DOWN
        self.d = direction

        self.c = colour
        self.num_bubbles = num_bubbles

        self.x = 0
        self.y = 0

        self.w = game.win_w
        self.h = game.win_h

        self.blocking = False

        self.bubble_r = game.win_w // num_bubbles
        mv = self.bubble_r

        self.num_bubbles_vert = game.win_h // self.bubble_r + 1

        self.bubble_speed = self.bubble_r / tick * 0.2

        if self.d == "LEFT":
            self.place_x = game.win_w
            self.place_y = None
            self.vel = (mv * -1, 0)

        elif self.d == "RIGHT":
            self.place_x = 0
            self.place_y = None
            self.vel = (mv, 0)

        elif self.d == "UP":
            self.place_x = None
            self.place_y = game.win_h
            self.vel = (0, mv * -1)

        elif self.d == "DOWN":
            self.place_x = None
            self.place_y = 0
            self.vel = (0, mv)

        else:
            raise AttributeError(f"{self.d} is not a valid direction, must be in (LEFT, RIGHT, UP, DOWN)")

        self.bubble_list = []
        self.surface = Surface((self.w, self.h))
        self.surface.fill(colours.colourkey)
        self.surface.set_colorkey(colours.colourkey)

        self.firsttick = True
        self.tick = move.frametick(tick=tick, game=game)

    def check_cover(self):
        check_bubbles = [b.max_size for b in self.bubble_list]

        if all(check_bubbles):
            for b in self.bubble_list:
                b.reverse()
            self.blocking = True

    def update_move(self, game):

        self.update_bubbles(game)

        if self.firsttick is False:
            self.check_cover()
            if len(self.bubble_list) == 0:
                self.kill()

        if not self.tick.get():
            return
        self.firsttick = False

        if self.place_y is None:
            if self.place_x > game.win_w or self.place_x < 0:
                return

            for y in range(self.num_bubbles_vert):
                new_b = self.bubble((self.place_x, y*self.bubble_r), self.bubble_r, self.bubble_speed, self.c)
                new_b.add_default_attr(game)

                self.bubble_list.append(new_b)

            self.place_x += self.vel[0]

        elif self.place_x is None:
            if self.place_y > game.win_h or self.place_y < 0:
                return

            for x in range(self.num_bubbles):
                new_b = self.bubble((x*self.bubble_r, self.place_y), self.bubble_r, self.bubble_speed, self.c)
                new_b.add_default_attr(game)

                self.bubble_list.append(new_b)

            self.place_y += self.vel[1]

    def update_bubbles(self, game):
        valid_bubbles = []
        for b in self.bubble_list:
            b.update_move(game)
            b.update_draw(self.surface)
            if not b.destroy:
                valid_bubbles.append(b)

        self.bubble_list = valid_bubbles

    def update_draw(self, game):
        # Will always blit at (0, 0) lol
        game.win.blit(self.surface, (self.x , self.y))
        self.surface.fill(colours.colourkey)
        self.surface.set_colorkey(colours.colourkey)


class screenwipe(sprite):
    layer = "FOREGROUND"
    persistent = True

    def __init__(self, direction, sprite, speed, colour, game):
        # LEFT, RIGHT, UP, DOWN
        self.d = direction

        self.c = colour

        self.sprite = sprite
        size = self.sprite.get_size()

        self.w = size[0]
        self.h = size[1]

        self.blocking = False
        self.firstframe = True

        if self.d == "LEFT":
            self.x = game.win_w
            self.y = 0
            self.vel = (speed * -1, 0)

        elif self.d == "RIGHT":
            self.x = self.w * -1
            self.y = 0
            self.vel = (speed, 0)

        elif self.d == "UP":
            self.x = 0
            self.y = game.win_h
            self.vel = (0, speed * -1)

        elif self.d == "DOWN":
            self.x = 0
            self.y = game.win_h * -1
            self.vel = (0, speed)

        else:
            self.d = "LEFT"
            self.x = game.win_w
            self.y = 0
            self.vel = (speed * -1, 0)

            print("SAVED SCREENWIPE")

    def update_move(self, game):
        self.x += self.vel[0]
        self.y += self.vel[1]

        if self.x > 0 and self.x < abs(self.vel[0]) * 2 and self.y == 0: # blocking out the whole screen
            self.blocking = True
            # Start loading level
        else:
            self.blocking = False

        if not self.firstframe:

            gamewin = (0, 0, game.win_w, game.win_h)

            if not self.x + self.w > gamewin[0] and not self.x < gamewin[0] + gamewin[2]:
                if not self.y + self.h > gamewin[1] and not self.y < gamewin[1] + gamewin[3]:
                    self.kill()

        self.firstframe = False

    def update_draw(self, game):
        # draw.rect(game.win, self.c, (self.x, self.y, self.w, self.h))
        game.win.blit(self.sprite, (self.x, self.y))
