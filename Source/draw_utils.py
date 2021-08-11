import random
from pygame import draw
from sprite_class import sprite


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


class screenwipe(sprite):
    layer = "FOREGROUND"
    persistent = True

    def __init__(self, direction, size, speed, colour, game):
        self.d = direction
        # left, right, up, down
        self.w = size[0]
        self.h = size[1]

        self.c = colour

        self.blocking = False
        self.firstframe = True

        if self.d == "LEFT":
            self.x = game.win_w
            self.y = 0
            self.vel = (speed * -1, 0)

        elif self.d == "RIGHT":
            self.x = game.win_w * -1
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

        if self.x == 0 and self.y == 0: # blocking out the whole screen
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
        draw.rect(game.win, self.c, (self.x, self.y, self.w, self.h))
