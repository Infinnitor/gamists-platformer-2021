import random
import draw_utils as draw_u


class colour_list():
    def __init__(c):

        c.fullred = (255, 0, 0)
        c.fullgreen = (0, 255, 0)
        c.fullblue = (0, 0, 255)

        c.red = (155, 35, 35)
        c.green = (35, 155, 35)
        c.blue = (35, 35, 155)

        c.pink = (255, 0, 255)
        c.purple = (155, 35, 155)
        c.fullcyan = (0, 255, 255)
        c.cyan = (35, 155, 155)
        c.teal = (35, 100, 100)
        c.fullyellow = (255, 255, 0)
        c.yellow = (155, 155, 35)

        c.black = (10, 10, 10)
        c.fullblack = (1, 1, 1)

        c.white = (255, 255, 255)

        c.colourkey = (0, 0, 0)

        c.full_list = (
            c.fullred,
            c.fullgreen,
            c.fullblue,
            c.red,
            c.green,
            c.blue,
            c.pink,
            c.purple,
            c.fullcyan,
            c.cyan,
            c.teal,
            c.fullyellow,
            c.yellow
        )

        c.primary = (
            c.fullred,
            c.fullgreen,
            c.fullblue,
            c.red,
            c.green,
            c.blue
        )

        switch_t = (
            (155, 35, 35),
            (155, 35, 90),
            (155, 35, 150),
            (115, 35, 155),
            (55, 35, 155),
            (35, 80, 155),
            (35, 120, 155),
            (35, 155, 130),
            (35, 155, 75),
            (45, 155, 35),
            (120, 155, 35),
            (155, 135, 35),
            (155, 90, 35),
            (155, 50, 35)
        )

        c.switch_list = []
        for i in range(len(switch_t)):
            base_c = switch_t[i]
            try:
                next_c = switch_t[i + 1]
            except IndexError:
                next_c = switch_t[0]

            c.switch_list.append(base_c)

            for l in range(25, 100, 25):
                c.switch_list.append(draw_u.rgb.lerp(base_c, next_c, l))

        c.switch_iter = random.randint(0, len(c.switch_list) - 1)

    def rand(c):
        return random.choice(c.full_list)

    def switch(c):
        c.switch_iter += 1
        try:
            switch_colour = c.switch_list[c.switch_iter]
        except IndexError:
            c.switch_iter = 0
            switch_colour = c.switch_list[c.switch_iter]

        return switch_colour


colours = colour_list()
