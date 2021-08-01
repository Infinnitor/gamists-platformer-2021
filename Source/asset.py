from pygame import image, mixer, Surface
from colour_manager import colours
import random


# This will actually do something later on trust me bro
def fix_path(p):
    return p


class spritesheet():
    def __init__(self, path, size):
        self.path = fix_path(path)
        self.sheet = image.load(self.path).convert()

        self.w = size[0]
        self.h = size[1]
        self.sheet_size = self.sheet.get_size()

        self.sprites = []
        for y in range(0, self.sheet_size[1], self.h):
            for x in range(0, self.sheet_size[0], self.w):
                self.sprites.append(self.get_region(x, y))

    def get_region(self, x, y):
        region = Surface((self.w, self.h))
        region.set_colorkey(colours.colourkey)

        region.blit(self.sheet, (0, 0), (x, y, self.w, self.h))
        return region

    def list(self):
        return self.sprites


class audio_manager():
    def __init__(self, sounds):
        if sounds is not None:
            self.sounds = {}
            for i, s in enumerate(sounds):
                self.sounds[s] = (sounds[s], i)
            mixer.set_num_channels(len(self.sounds))

        else:
            self.sounds = None

    def play(self, name):

        assert name in self.sounds, f"{name} is an undefined sound"
        s = self.sounds[name]

        mixer.Channel(s[1]).play(s[0])


class texture_manager():
    def __init__(self):
        self.platform_tex = spritesheet('data/sprites/textures/platform_spritesheet.png', (20, 20)).list()

    def platform(self):
        return random.choice(self.platform_tex)


def init():
    global sound; global texture; global AMONGUS;
    sound = audio_manager(None)
    texture = texture_manager()

    AMONGUS = image.load(fix_path(('data/sprites/textures/amongus.png')))
