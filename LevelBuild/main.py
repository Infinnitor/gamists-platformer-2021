# Rectfinder linemethod
from gameinfo import game_info, pygame, sprite, random


def text_clean(file):
    text = file.readlines()
    valid_text = []
    for f in range(len(text)):
        if text[f].startswith("#"):
            continue
        text[f] = text[f].replace("\n", "")

        if not text[f].replace(" ", "") == "":
            valid_text.append(text[f])

    return valid_text


def read_brackets(string):
    b_values = []
    for iter, char in enumerate(string):
        if char == "(":
            b_iter = iter
            b_char = ""
            while b_char != ")":
                b_iter += 1
                b_char = string[b_iter]
            b_values.append(string[iter + 1 : b_iter])

    return b_values


class text_config():
    def __init__(self, filename):
        file = text_clean(open(filename, 'r'))

        values = {}
        for val in file:
            val = val.replace(" ", "")
            k, char = val.split(":")
            k = tuple([int(i) for i in read_brackets(k)[0].split(",")])
            values[k] = char

        self.dict = values


class grid_square(sprite):
    layer = "GRID"

    def __init__(self, x, y, side, element):
        self.x = x
        self.y = y
        self.side = side

        self.c = element
        self.element = None
        for col in config.dict:
            if col == element:
                self.element = config.dict[col]

        if self.element is None:
            print(f"ERROR: unrecognised colour {element}, at X: {self.x} Y: {self.y}")
            self.element = '!'
            self.c = (255, 255, 0)

    def update_draw(self, game):
        if self.element == '!':
            pygame.draw.rect(game.win, game.bg, (self.x * self.side, self.y * self.side, self.side, self.side))
            pygame.draw.circle(game.win, self.c, (self.x * self.side + self.side//2, self.y * self.side + self.side//2), self.side * 0.3)

        else:
            pygame.draw.rect(game.win, self.c, (self.x * self.side, self.y * self.side, self.side, self.side))


game = game_info(
                name="LevelBuilder",
                win_w=1280,
                win_h=720,
                user_w=1280,
                user_h=720,
                bg=(1, 1, 1),
                framecap=False,
                show_framerate=False,
                quit_key=pygame.K_ESCAPE)

config = text_config('colour_config.txt')

level_image = pygame.image.load('level.png')
level_image.set_colorkey((0, 0, 0))

l_w, l_h = level_image.get_size()

for y in range(l_h):
    for x in range(l_w):
        px_colour = level_image.get_at((x, y))
        game.add_sprite(grid_square(x, y, 20, px_colour))

assert len(game.sprites["GRID"]) <= l_w * l_h

while game.run:
    game.update_keys()

    game.update_draw()

    game.update_scaled()

    game.update_state()
