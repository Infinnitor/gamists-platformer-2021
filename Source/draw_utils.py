import random
from pygame import draw


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
