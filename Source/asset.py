from pygame import image, mixer, Surface
from colour_manager import colours
import random
import os
import sys


if getattr(sys, 'frozen', False):
    EXE_PATH = os.path.dirname(sys.executable)
elif __file__:
    EXE_PATH = os.path.dirname(__file__)


def fix_path(relative_path):
    abs_path = os.path.join(EXE_PATH, relative_path)

    if sys.platform in ('linux', 'linux2'):
        abs_path = abs_path.replace('\\', '/')
    else:
        abs_path = abs_path.replace('/', '\\')

    return abs_path


# Wacky spritesheet innit??
class spritesheet():
    def __init__(self, path, size):
        self.path = fix_path(path)

        # Convert it to save time when blitting
        self.sheet = image.load(self.path).convert()

        # Size of each sprite in the size
        self.w = size[0]
        self.h = size[1]
        self.sheet_size = self.sheet.get_size()

        # Iterate through spritesheet to find sprites
        self.sprites = []
        for y in range(0, self.sheet_size[1], self.h):
            for x in range(0, self.sheet_size[0], self.w):
                self.sprites.append(self.get_region(x, y))

    # Pygame is silly hehe
    # To find get a given region it has to be blitted to a surface
    def get_region(self, x, y):
        region = Surface((self.w, self.h))
        region.set_colorkey(colours.colourkey)

        region.blit(self.sheet, (0, 0), (x, y, self.w, self.h))
        return region

    def list(self):
        return self.sprites


class audio_manager():
    def __init__(self, sounds):

        self.sounds = sounds
        # Create a dictionary of sounds
        if sounds is not None:
            self.sounds = {}
            for i, s in enumerate(sounds):
                self.sounds[s] = (sounds[s], i)

            # In order to play sounds on top of each other, one channel is created for each sound
            mixer.set_num_channels(len(self.sounds))

    # Sound is played in its given channel
    def play(self, name):

        assert name in self.sounds, f"{name} is an undefined sound"
        s = self.sounds[name]

        mixer.Channel(s[1]).play(s[0])


class texture_manager():
    def __init__(self):
        self.platform_tex = spritesheet('data/sprites/textures/platform_rachel.png', (20, 20))
        self.amogus = spritesheet(fix_path(('data/sprites/textures/amongus.png')), (20, 20))

        self.hazard_tex = spritesheet('data/sprites/textures/hazard_spritesheet.png', (20, 20))

        self.screenwipe = image.load('data/sprites/ui/screenwipe_RED.png')
        self.platform_map = image.load(fix_path('data/sprites/textures/ape_out.png'))
        self.bg_texture = image.load(fix_path('data/sprites/textures/ape_bg.png'))

    def hazard(self):
        return random.choice(self.hazard_tex.list())

    def bean_texture(self):
        return random.choice(self.platform_tex.list())

    def amongus(self):
        return random.choice(self.amogus.list())


class sprite_manager():
    def __init__(self):
        checkpoint = spritesheet('data/sprites/level/checkpoint_spritesheet.png', (40, 40)).list()
        self.checkpoint_false = checkpoint[0]
        self.checkpoint_true = checkpoint[1]


def init():
    global SOUND; global TEXTURE; global AMONGUS; global SPRITE;
    SOUND = audio_manager(None)
    TEXTURE = texture_manager()
    SPRITE = sprite_manager()

    AMONGUS = image.load(fix_path(('data/sprites/textures/amongus.png')))
