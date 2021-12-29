# MODIFICATIONS:
# - self.sprites replace with 2D array for gridsquares
# - Camera Removed

# DO NOT COPY LOL

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import sys
import math
import time
import random
import pygame
pygame.font.init()


class sprite():

    def __repr__(self):
        self.highlight = 30
        return f"{self.layer} at position {self.x}, {self.y}"

    def update_move(self, game):
        pass

    def update_draw(self, game):
        pass

    def update_destroy(self, game):
        pass

    def update_highlight(self, game):
        if self.highlight > 0:
            self.draw_highlight(game)
            self.highlight -= 1

    def draw_highlight(self, game):
        try:
            highlight_r = self.r
        except AttributeError:
            highlight_r = 10

        pygame.draw.circle(game.win, (35, 155, 35), (self.x, self.y), highlight_r)

    def add_default_attr(self, game):
        self.destroy = False
        self.destroying = False
        self.highlight = 0

    def kill(self):
        self.destroy = True

    def onscreen(self, game):
        if self.x < 0 or self.x > game.win_w:
            return False
        if self.y < 0 or self.y > game.win_h:
            return False

        return True

    def onscreen_info(self, game):
        if self.x < 0 or self.x > game.win_w:
            return "X"
        if self.y < 0 or self.y > game.win_h:
            return "Y"

        return ""

    def center_image_pos(self, sprite, pos):
        i = sprite.get_size()

        x = pos[0] - (i[0] // 2)
        y = pos[1] - (i[0] // 2)

        return x, y

    def blit_rotate(self, image, angle, game):
        img = pygame.transform.rotate(image, angle)

        b_x = self.x - img.get_width()//2
        b_y = self.y - img.get_height()//2

        game.win.blit(img, (b_x, b_y))


class game_info():
    def __init__(self, name, win_w, win_h, user_w, user_h, bg, sounds=None, framecap=False, show_framerate=False, quit_key=None):
        self.win_w = win_w
        self.win_h = win_h

        self.user_w = user_w
        self.user_h = user_h

        self.win_scale = pygame.display.set_mode((user_w, user_h))
        pygame.display.set_caption(name)
        self.win = pygame.Surface((win_w, win_h))

        if sounds:
            self.sounds = {}
            for i, s in enumerate(sounds):
                self.sounds[s] = (sounds[s], i)
            pygame.mixer.set_num_channels(len(self.sounds))

        else:
            self.sounds = None

        self.bg = bg
        self.run = True

        self.clock = pygame.time.Clock()

        self.keys = pygame.key.get_pressed()
        self.mouse = pygame.mouse.get_pressed()
        self.mouse_pos = pygame.mouse.get_pos()
        self.update_keys()

        self.frames = 0
        self.framecap = framecap
        self.show_framerate = show_framerate

        self.start_time = time.time()
        self.quit_key = quit_key

        self.shake_x = 0
        self.shake_y = 0
        self.shake = False

        self.particles = []
        self.sprites = []

        self.font = pygame.font.SysFont("Comic sans", 30)

    # Function that converts an orientation into actual numbers
    def orientate(self, h=False, v=False):

        h_dict = {
            "Left" : 0,
            "Left-Center" : self.win_w // 4,
            "Center" : self.win_w // 2,
            "Right-Center" : (self.win_w // 4) * 3,
            "Right" : self.win_w,
            "Rand" : random.randint(0, self.win_w)
            }

        v_dict = {
            "Top" : 0,
            "Top-Center" : self.win_h // 4,
            "Center" : self.win_h // 2,
            "Bottom-Center" : (self.win_h // 4) * 3,
            "Bottom" : self.win_h,
            "Rand" : random.randint(0, self.win_h)
            }

        # We have to check that the orientation exists first
        if h:
            assert h in h_dict, f"{h} is not a valid orientation"
        if v:
            assert v in v_dict, f"{v} is not a valid orientation"

        if h and v:
            return (h_dict[h], v_dict[v])
        elif h and not v:
            return h_dict[h]
        elif v and not h:
            return v_dict[v]

        return False # Safety Clause

    def playsound(self, name):

        assert name in self.sounds, f"{name} is an undefined sound"
        s = self.sounds[name]

        pygame.mixer.Channel(s[1]).play(s[0])

    def purge_sprites(self):
        for layer in range(len(self.sprites)):
            self.sprites[layer] = []

    def init_screenshake(self, magnitude, len, rand=True, spread=False):
        self.shake = True
        self.shake_index = 0

        pos1 = 0 - magnitude
        pos2 = magnitude

        if rand and spread:
            pos1 = int(pos1 * random.uniform(spread[0], spread[1]))
            pos2 = int(pos2 * random.uniform(spread[0], spread[1]))

        bb_temp = [
            (pos1, pos1),
            (pos2, pos1),
            (pos1, pos2),
            (pos2, pos2)
            ]

        self.bounding_box = [bb_temp[i % 4] for i in range(len)]

        if rand:
            random.shuffle(self.bounding_box)

        self.bounding_box.append((0, 0))

    def check_mouse(self, button, buffer=False, timebuffer=False):
        if timebuffer:
            if self.frames % timebuffer != 0 and self.last_mouse[button]:
                return False

        if buffer:
            if self.last_mouse[button]:
                return False
            elif self.mouse[button]:
                return True
        elif self.mouse[button]:
            return True

    def check_key(self, *args, buffer=False, all_press=False, timebuffer=False):

        if timebuffer:
            if self.frames % timebuffer != 0:
                for givenkey in args:
                    if self.last_keys[givenkey]:
                        return False

        fullkeys = 0
        for givenkey in args:
            if buffer:
                if self.last_keys[givenkey]:
                    return False

            if self.keys[givenkey]:
                if all_press:
                    fullkeys += 1
                else:
                    fullkeys = len(args)
                    break

        if fullkeys >= len(args):
            return True

        return False # Safety Clause

    def update_screenshake(self):
        if not self.shake:
            return

        bb_iter = self.bounding_box[self.shake_index]
        self.shake_x = bb_iter[0]
        self.shake_y = bb_iter[1]

        if self.shake_index < len(self.bounding_box) - 1:
            self.shake_index += 1
        else:
            self.shake = False

    def update_particles(self):
        if len(self.particles):
            p_survive = []
            for p in self.particles:
                if p.destroy:
                    continue
                p.update_move()
                p.update_draw(self)
                p_survive.append(p)

            self.particles = p_survive

    def update_keys(self):
        self.last_keys = self.keys
        self.last_mouse = self.mouse

        self.keys = pygame.key.get_pressed()
        self.mouse = pygame.mouse.get_pressed()

        m = pygame.mouse.get_pos()
        w_ratio = self.win_w / self.user_w
        h_ratio = self.win_h / self.user_h

        self.mouse_pos = (m[0] * w_ratio, m[1] * h_ratio)

    def bg_kill(self, obj):
        for iter, s in enumerate(self.sprites["BACKGROUND"]):
            if s is obj:
                for d in self.sprites["BACKGROUND"][0:iter]:
                    d.kill()

        self.bg = obj.c
        obj.kill()

    def update_draw(self):

        for y, row in enumerate(self.sprites):
            valid_sprites = []
            for x in row:
                x.update_move(self)
                if not x.destroy:
                    valid_sprites.append(x)
            self.sprites[y] = valid_sprites

        for y, row in enumerate(self.sprites):
            valid_sprites = []
            for x in row:
                x.update_draw(self)
                if not x.destroy:
                    valid_sprites.append(x)
            self.sprites[y] = valid_sprites

        self.update_screenshake()

    # Function for scaling the design screen to the target screen
    def update_scaled(self):

        # Lock framerate
        if self.framecap:
            self.clock.tick(self.framecap)

        # Scale the design screen to the size of the target screen
        frame = pygame.transform.scale(self.win, (self.user_w, self.user_h))

        # Blit scaled design screen to target screen, plus screenshake
        self.win_scale.blit(frame, (self.shake_x, self.shake_y))

        # Update screen display
        pygame.display.flip()

        # Delete everything on the screen for next loop
        self.win.fill(self.bg)
        self.win_scale.fill(self.bg)

    def update_state(self):

        self.frames += 1
        self.elapsed_time = time.time() - self.start_time

        self.framerate = self.frames / self.elapsed_time
        if self.show_framerate:
            print(self.framerate, end="\r")

        if not self.quit_key == None:
            if self.check_key(self.quit_key):
                self.run = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False


if __name__ == "__main__":
    game = game_info(
                    name="Launched from module py file",
                    win_w=1280,
                    win_h=720,
                    user_w=1920,
                    user_h=1080,
                    bg=(0, 0, 0),
                    framecap=60,
                    show_framerate=True,
                    quit_key=pygame.K_ESCAPE)

    while game.run:
        game.update_keys()
        game.update_draw()

        if game.check_key(pygame.K_LEFT, pygame.K_RIGHT, all_press=True):
            print("BOTH DOWN")

        if game.check_key(pygame.K_d, pygame.K_a):
            print("ALIAS")

        game.update_scaled()
        game.update_state()

    pygame.quit()
