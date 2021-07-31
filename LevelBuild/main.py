# Rectfinder linemethod
from gameinfo import game_info, pygame, sprite, random
# pygame.font.init()

import tkinter
import tkinter.filedialog

import glob


def prompt_file():
    """Create a Tk file dialog and cleanup when finished"""
    top = tkinter.Tk()
    top.withdraw()  # Hide window
    file_name = tkinter.filedialog.askopenfilename(parent=top, defaultextension='.png')
    top.destroy()
    return file_name


def prompt_dir():
    """Create a Tk file dialog and cleanup when finished"""
    top = tkinter.Tk()
    top.withdraw()  # Hide window
    file_name = tkinter.filedialog.askdirectory(parent=top)
    top.destroy()
    return file_name


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


def clear_file(name):
    file = open(f"levels/output/{name}.txt", "w+")
    file.write("")
    file.close()


def build_text(gridrect, name):
    file = open(f"levels/output/{name}.txt", "a+")
    target_element = gridrect[0].start_element

    u_x, u_y = gridrect[0].upper()
    l_x, l_y = gridrect[-1].lower()

    rect_w = l_x - u_x
    rect_h = l_y - u_y

    # print(f"{rect_w},  {rect_h}")
    out_text = f"({u_x}, {u_y}) ({rect_w}, {rect_h}) ({target_element})\n"
    file.write(out_text)

    file.close()


# Function for finding out the initial parameters of a potential rectangle, given a starting tile
def rect_trailpath(game, start_tile):
    x = start_tile.x
    y = start_tile.y

    trail = []
    c_tile = start_tile

    # Loop on the X until it hits a tile that is not of the same element
    while c_tile.element == start_tile.element:
        trail.append(c_tile)
        x += 1
        try:
            c_tile = game.sprites[y][x]

        # Break if it hits the edge of the level
        except IndexError:
            break

    return trail


# Function that finds another row in a rect, given a trailpath
def rect_trail(game, given_trail):

    target_element = given_trail[0].element

    # The rect must not go outside these boundaries, or else it will no longer be a rectangle
    max_x = given_trail[-1].x
    min_x = given_trail[0].x

    # Starting pos
    x = given_trail[0].x
    y = given_trail[0].y + 1

    # If the starting Y is bigger than the level height, the trail is invalid
    if y >= game.level_height:
        return None

    trail = []
    c_tile = game.sprites[y][x]

    # Create an unbroken line with a while loop
    while c_tile.element == target_element:
        trail.append(c_tile)
        x += 1
        try:
            c_tile = game.sprites[y][x]

        # Except an IndexError because order of events is wonky
        except IndexError:
            pass
            # print(f"INDEXERROR Max: {max_x}, X: {x}, Y: {y}")

        # Check if length of trail is equal to that of the given trailpath
        if len(trail) == len(given_trail):
            # print(f"LENGTH COMP Max: {max_x}, X: {x}, Y: {y}")

            # Check what the elements are to either side of the trail
            try:
                # Handle ending the rect differently if the algo is STRATA
                if game.algorithm == "STRATA":
                    # If they are not the target element, they are valid
                    # Otherwise, the rect is infringing on space that could be used by other rects

                    # If this is the case, declare the current trail to be invalid
                    if game.sprites[y][max_x + 1].element == target_element:
                        return None
                    elif game.sprites[y][min_x - 1].element == target_element:
                        return None
            except IndexError:
                pass

            return trail

    # Return None if while loop is broken by incorrect element
    # print(f"NONE Max: {max_x}, X: {x}, Y: {y}")
    return None


# Function for finding a rectangle in level.png, given a target element
def rect_finder(given_e, game):

    # Iterate through 2Darray
    for row in game.sprites:
        for tile in row:

            # Begin a new rect trail if the element of the current tile matches the given element
            if tile.element == given_e:
                rect_trails = []

                # Create a trailpath to define the width of the rect
                start_trail = rect_trailpath(game, tile)
                rect_trails.extend(start_trail)

                # Create a rect trail based on the parameters of the trailpath
                newtrail = rect_trail(game, start_trail)

                # Repeat until you get an invalid trail
                # Invalid trail means that the rect can no longer be drawn further
                while newtrail is not None:
                    rect_trails.extend(newtrail)
                    print(f"Found rect at {newtrail[0].x}, {newtrail[0].y}")

                    newtrail = rect_trail(game, newtrail)

                # Colour and remove all grid squares from the list of potential rects
                for tile in rect_trails:
                    tile.c = (0, 155, 0)
                    tile.element = "Found"

                return rect_trails

    # Return None if you looped through the list without success
    return None


# Grid square class
class grid_square(sprite):
    layer = "GRID"

    def __init__(self, pos, size, element):

        # Position in the grid
        self.x = pos[0]
        self.y = pos[1]

        # Size of the gridsquare when drawing it
        self.w = size[0]
        self.h = size[1]

        # Hardcoded size of a tile in the final game
        self.tile_side = 20

        self.c = element
        self.element = None
        self.warn = False

        # Check for corresponding string to the given element
        for col in game.config.dict:
            if col == element:
                self.element = game.config.dict[col]

        # If invalid, print an error and set self.element to GroundTerrain
        if self.element is None:
            print(f"ERROR: unrecognised colour {element}, at X: {self.x} Y: {self.y}")

            self.element = "GroundTerrain"
            self.c = (10, 10, 10)
            # Set self.warn to True so that a warning is drawn
            self.warn = True

        self.start_element = self.element

    def update_draw(self, game):
        if game.draw_grid is False:
            return

        pygame.draw.rect(game.win, self.c, (self.x * self.w, self.y * self.h, self.w, self.h))

        # Draw a warning circle if neccessary
        if self.warn is True:
            pygame.draw.circle(game.win, (255, 255, 0), (self.x * self.w + self.w//2, self.y * self.h + self.h//2), self.w * 0.3)

    def upper(self):
        return [self.x * self.tile_side, self.y * self.tile_side]

    def lower(self):
        return [(self.x * self.tile_side) + self.tile_side, (self.y * self.tile_side) + self.tile_side]


class button(sprite):
    def __init__(self, pos, size, name, colours):
        self.x = pos[0]
        self.y = pos[1]

        self.w = size[0]
        self.h = size[1]

        self.name = name
        self.colours = colours
        self.c = colours[0]

        self.flash = 0

    def mouseover(self, game):
        m_x, m_y = game.mouse_pos
        if m_x > self.x and m_x < self.x + self.w:
            if m_y > self.y and m_y < self.y + self.h:
                return True

        return False

    def update_move(self, game):

        if self.mouseover(game):
            if game.check_mouse(0, buffer=True):
                self.flash = 30
            else:
                self.c = self.colours[1]
        else:
            self.c = self.colours[0]

        if self.flash > 0:
            if self.flash == 15:
                self.click(game)
            self.flash -= 1
            self.c = self.colours[2]

    def update_draw(self, game):
        pygame.draw.rect(game.win, self.c, (self.x, self.y, self.w, self.h))

        text = game.font.render(self.name, False, (255, 255, 255))

        text_center = (text.get_width()//2, text.get_height()//2)
        button_cx = (self.x + self.w//2) - text_center[0]
        button_cy = (self.y + self.h//2) - text_center[1]

        game.win.blit(text, (button_cx, button_cy))

    def click(self, game):
        if self.name == "LOAD LEVEL":
            levelpath = prompt_file()

            if levelpath and levelpath.endswith('.png'):
                rects = mainloop(game, levelpath)
                if rects is not None:
                    level_name = levelpath.split('/')[-1]
                    clear_file(level_name.replace('.png', ''))
                    for platform in rects:
                        build_text(platform, level_name.replace('.png', ''))

            else:
                print("FAILED")

        elif self.name == "LOAD MULTIPLE":
            leveldir = prompt_dir()

            if leveldir:
                level_files = glob.glob(leveldir + "/*.png")
                for i in range(len(level_files)):
                    level_files[i] = level_files[i].replace("\\", "/")

                for f in level_files:
                    rects = mainloop(game, f)
                    if rects is not None:
                        level_name = f.split('/')[-1]
                        clear_file(level_name.replace('.png', ''))
                        for platform in rects:
                            build_text(platform, level_name.replace('.png', ''))
            else:
                print("FAILED")

        elif self.name.startswith("ALGORITHM"):
            if self.name == "ALGORITHM: STRATA":
                self.name = "ALGORITHM: DROP"
                game.algorithm = "DROP"
            else:
                self.name = "ALGORITHM: STRATA"
                game.algorithm = "STRATA"

        elif self.name.startswith("DRAW GRID"):
            if self.name == "DRAW GRID: TRUE":
                self.name = "DRAW GRID: FALSE"
                game.draw_grid = False
            else:
                self.name = "DRAW GRID: TRUE"
                game.draw_grid = True


def mainloop(game, levelpath):
    game.config = text_config('colour_config.txt')

    level_image = pygame.image.load(levelpath)
    # level_image.set_colorkey((0, 0, 0))

    padded_level = pygame.Surface(())

    pygame.draw.rect()

    game.level_width, game.level_height = level_image.get_size()

    gridsquare_size = (game.win_w / game.level_width, game.win_h / game.level_height)

    rows = []
    for y in range(game.level_height):
        yrow = []
        for x in range(game.level_width):
            px_colour = level_image.get_at((x, y))

            obj = grid_square((x, y), gridsquare_size, px_colour)
            obj.add_default_attr(game)
            yrow.append(obj)

        rows.append(yrow)

    game.sprites = rows

    found_rects = []
    elements = list(game.config.dict.values())
    elements.remove("Background")
    e_iter = 0

    while game.run:

        game.update_keys()


        if game.frames % int(gridsquare_size[0]) == 0:
            a_rect = rect_finder(elements[e_iter], game)
            if a_rect is not None:
                found_rects.append(a_rect)
            else:
                e_iter += 1
                if e_iter >= len(elements):
                    pygame.time.delay(500)
                    game.purge_sprites()
                    return found_rects

        game.update_draw()

        game.update_scaled()

        game.update_state()


def mainmenu(game):
    load = button((530, 200), (200, 60), "LOAD LEVEL", [(90, 10, 10), (120, 20, 20), (255, 35, 35)])
    load_all = button((530, 280), (200, 60), "LOAD MULTIPLE", [(90, 10, 10), (120, 20, 20), (255, 35, 35)])

    algo = button((500, 360), (260, 60), "ALGORITHM: STRATA", [(90, 10, 10), (120, 20, 20), (255, 35, 35)])
    game.algorithm = "STRATA"

    draw_grid = button((500, 440), (260, 60), "DRAW GRID: TRUE", [(90, 10, 10), (120, 20, 20), (255, 35, 35)])
    game.draw_grid = True

    buttons = [load, load_all, algo, draw_grid]

    while game.run:
        game.update_keys()

        for b in buttons:
            b.update_move(game)
            b.update_draw(game)

        game.update_draw()

        game.update_scaled()

        game.update_state()


game = game_info(
                name="LevelBuilder",
                win_w=1280,
                win_h=720,
                user_w=1280,
                user_h=720,
                bg=(255, 255, 255),
                framecap=False,
                show_framerate=False,
                quit_key=pygame.K_ESCAPE)


mainmenu(game)
