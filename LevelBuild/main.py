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


def rect_trailpath(game, start_tile):
    x = start_tile.x
    y = start_tile.y

    trail = []
    c_tile = start_tile

    while c_tile.element == start_tile.element:
        c_tile.c = (255, 40, 255)
        trail.append(c_tile)
        x += 1
        try:
            c_tile = game.sprites[y][x]

        except IndexError:
            break

    return trail


def rect_trail(game, given_trail):
    target_element = given_trail[0].element

    max_x = given_trail[-1].x

    x = given_trail[0].x
    y = given_trail[0].y + 1
    if y >= level_height:
        return None

    trail = []
    c_tile = game.sprites[y][x]

    while c_tile.element == target_element and x <= max_x:
        trail.append(c_tile)
        x += 1
        try:
            c_tile = game.sprites[y][x]
        except IndexError:
            print(f"INDEXERROR Max: {max_x}, X: {x}, Y: {y}")

        if len(trail) == len(given_trail):
            print(f"LENGTH COMP Max: {max_x}, X: {x}, Y: {y}")
            return trail

    print(f"NONE Max: {max_x}, X: {x}, Y: {y}")
    return None


def rect_finder(given_e, game):
    for y, row in enumerate(game.sprites):
        for x, tile in enumerate(row):
            if tile.element == given_e:
                rect_trails = []
                start_trail = rect_trailpath(game, tile)
                rect_trails.extend(start_trail)

                newtrail = rect_trail(game, start_trail)

                while newtrail is not None:
                    rect_trails.extend(newtrail)

                    newtrail = rect_trail(game, newtrail)

                for tile in rect_trails:
                    tile.c = (0, 155, 0)
                    tile.element = "Found"

                return rect_trails

    return None


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

level_width, level_height = level_image.get_size()

rows = []
for y in range(level_height):
    yrow = []
    for x in range(level_width):
        px_colour = level_image.get_at((x, y))

        obj = grid_square(x, y, 20, px_colour)
        obj.add_default_attr(game)
        yrow.append(obj)

    rows.append(yrow)

game.sprites = rows

found_rects = []

while game.run:

    game.update_keys()

    if game.check_key(pygame.K_SPACE, buffer=True):
        a_rect = rect_finder("GroundTerrain", game)
        if a_rect is not None:
            found_rects.append(a_rect)

    game.update_draw()

    game.update_scaled()

    game.update_state()
