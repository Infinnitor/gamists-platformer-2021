from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from sprite_class import sprite

import math
import time
import random
import pygame
pygame.font.init()


class gameloop_manager(sprite):
    layer = "MANAGER"

    def __init__(self, loop_func, *func_args, reset_key=pygame.K_r):
        self.func = loop_func
        self.func_args = func_args

        self.current_loop = loop_func.__name__

        self.reset_key = reset_key

    def update_move(self, game):
        if game.check_key(self.reset_key, buffer=True):
            game.purge_sprites()
            self.func(*self.func_args)


def gameloop(setup):
    def run_loop(game, *args):
        setup(game, *args)
        # game.add_sprite(gameloop_manager(setup, game, *args))

        while game.run:
            game.update_keys()
            game.update_draw()
            game.update_scaled()
            game.update_state()

        pygame.quit()

    return run_loop


class game_info():
    def __init__(self, name, win_w, win_h, user_w, user_h, bg, framecap=False, show_framerate=False, quit_key=None):
        self.win_w = win_w
        self.win_h = win_h

        self.user_w = user_w
        self.user_h = user_h

        self.win_scale = pygame.display.set_mode((user_w, user_h))
        pygame.display.set_caption(name)
        self.win = pygame.Surface((win_w, win_h))

        self.bg = bg
        self.run = True

        self.clock = pygame.time.Clock()

        self.keys = pygame.key.get_pressed()
        self.mouse = pygame.mouse.get_pressed()
        self.mouse_pos = pygame.mouse.get_pos()
        self.update_keys()

        self.frames = 0
        self.framerate = 0

        self.framecap = framecap
        self.show_framerate = show_framerate

        self.start_time = time.time()
        self.last_frame_time = time.time()
        self.delta_time = 1

        self.quit_key = quit_key

        self.shake_x = 0
        self.shake_y = 0
        self.shake = False

        self.font_name = None
        self.font_size = self.win_w // 50
        self.FONT = pygame.font.Font(self.font_name, self.font_size)
        self.render_text = []

        self.sprites = {
                        "MANAGER" : [],
                        "CAMERA" : [],
                        "BACKGROUND" : [],
                        "LOWPARTICLE" : [],
                        "TERRAIN": [],
                        "HIGHPARTICLE" : [],
                        "UI" : [],
                        "FOREGROUND" : []}

    def add_sprite(self, new_sprite):
        new_sprite.add_default_attr(self)

        try:
            self.sprites[new_sprite.layer].append(new_sprite)
        except KeyError:
            self.sprites[new_sprite.layer] = [new_sprite]

    def purge_sprites(self, *layers, preserve=[]):
        if not layers:
            for layer in self.sprites:
                if layer in preserve:
                    continue
                self.sprites[layer] = []

        else:
            for l in layers:
                if layer in preserve:
                    continue
                self.sprites[l] = []

    def init_screenshake(self, magnitude, len, rand=True, spread=False):
        self.shake = True
        self.shake_index = 0

        pos1 = 0 - magnitude
        pos2 = magnitude

        if spread:
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

    def update_keys(self):
        self.last_keys = self.keys
        self.last_mouse = self.mouse

        self.keys = pygame.key.get_pressed()
        self.mouse = pygame.mouse.get_pressed()

        m = pygame.mouse.get_pos()
        w_ratio = self.win_w / self.user_w
        h_ratio = self.win_h / self.user_h

        self.mouse_pos = (m[0] * w_ratio, m[1] * h_ratio)

    def add_text(self, string, c=(255, 255, 255)):
        text_img = self.FONT.render(str(string), False, c)
        self.render_text.append(text_img)

    def update_draw(self):

        for c in self.sprites:
            valid_sprites = []
            for s_move in self.sprites[c]:
                if not s_move.destroying:
                    s_move.update_move(self)

                if not s_move.destroy:
                    valid_sprites.append(s_move)

            self.sprites[c] = valid_sprites

        for layer in self.sprites:
            for s_draw in self.sprites[layer]:
                if s_draw.destroying:
                    s_draw.update_destroy(self)
                else:
                    s_draw.update_draw(self)

        topmost = self.SELECTION_MANAGER.select_element
        if topmost is not None:
            if topmost.destroy is False:
                topmost.update_draw(self)

        for y, f in enumerate(self.render_text):
            y_pos = (y * self.font_size) + (self.font_size * 2)
            self.win.blit(f, (self.font_size * 2, y_pos))
        self.render_text = []

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

        self.delta_time = time.time() - self.last_frame_time

        self.last_frame_time = time.time()
        self.elapsed_time = time.time() - self.start_time

        self.framerate = 1 / self.delta_time

        if self.show_framerate:
            print(self.framerate, end="\r")
            self.add_text(self.framerate, (255, 255, 255))

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
