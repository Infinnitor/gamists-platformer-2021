from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from sprite_class import sprite
import draw_utils as drawu

import camera
import level_elements as level
import pyconfig

from asset import fix_path
import asset

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
        game.add_sprite(gameloop_manager(setup, game, *args))

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

        self.particles = drawu.particle_shortcuts(self)

        self.sprites = {
                        "BACKGROUND" : [],
                        "LOWPARTICLE" : [],
                        "CHECKPOINTS" : [],
                        "PLAYER": [],
                        "LEVELTRANSITION" : [],
                        "TERRAIN": [],
                        "HAZARD" : [],
                        "ENEMY" : [],
                        "HIGHPARTICLE" : [],
                        "CAMERACOLLIDER" : [],
                        "UI" : [],
                        "FOREGROUND" : []}

        self.camera_obj = camera.game_camera((0, 0), (self.win_w, self.win_h))
        self.oncam_sprites = []

    def load_level(self, name, player_spawn=False):
        levelpath = f"data/levels/{name}"

        def flagged(f):
            if self.levelflags.get(f):
                return True
            return False

        level_text, self.levelflags = pyconfig.text_level(levelpath)

        level_classes = {
            "GroundTerrain" : level.platform,
            "CameraCollider" : level.camera_collider,
            "Checkpoint" : level.checkpoint,
            "Hazard" : level.hazard,
            "LevelTransition" : level.level_transition,
            "Background" : level.background,
        }

        self.spawnkeys = {}

        # Define defaults for theme
        map = None
        platform_BG = asset.TEXTURE._blank
        level_theme = "MAIN"

        if flagged("!level_theme"):
            level_theme = self.levelflags["!level_theme"]
            assert level_theme in asset.VALID_LEVELTHEMES, f"{level_theme} is an invalid level theme. Must be in {asset.VALID_LEVELTHEMES}"

            if level_theme == "APEOUT" and flagged("!platform_map"):
                platform_BG = asset.TEXTURE.platform_map

        if flagged("!platform_map"):
            map_size = pyconfig.read_brackets(self.levelflags["!platform_map"])
            map_size = [int(i) for i in map_size[0].split(",")]

            map = pygame.Surface(map_size)
            pbg_x, pbg_y = platform_BG.get_size()

            # Made a surface the size of the entire level, with a repeated texture on it
            for y in range(0, (map_size[1] // pbg_y) * pbg_y + pbg_y, pbg_y):
                for x in range(0, (map_size[0] // pbg_x) * pbg_x + pbg_x, pbg_x):
                    map.blit(platform_BG, (x, y))

        self.purge_sprites("CHECKPOINTS", "TERRAIN", "HAZARD", "LEVELTRANSITION", "CAMERACOLLIDER", "BACKGROUND", "HIGHPARTICLE", "LOWPARTICLE")

        surface_sprites = ("GroundTerrain", "Hazard", "Background")

        for pos, size, sprite_type, args in level_text:
            if player_spawn is True:
                if sprite_type == "Checkpoint" or sprite_type == "Spawnkey":
                    self.PLAYER.x = pos[0]
                    self.PLAYER.y = pos[1]

                    self.PLAYER.set_spawn(pos)

                    # We only want this to happen once
                    player_spawn = False

            if sprite_type == "Spawnkey":
                key = args[0]

                self.spawnkeys[key] = pos
                continue

            if args:
                level_e = level_classes[sprite_type](pos, size, *args)
            else:
                level_e = level_classes[sprite_type](pos, size)
            level_e.leveltheme = level_theme

            if sprite_type in surface_sprites:
                level_e.generate_surface(map)

            self.add_sprite(level_e)

        self.oncam_sprites = []
        for layer in self.sprites:
            for s in self.sprites[layer]:
                self.oncam_sprites.append(s)

        if flagged("!camera_start"):
            new_cam_pos = pyconfig.read_brackets(self.levelflags["!camera_start"])
            new_x, new_y = [int(i) for i in new_cam_pos[0].split(",")]

            self.camera_obj.x = new_x
            self.camera_obj.y = new_y
        else:
            self.camera_obj.x = self.PLAYER.x
            self.camera_obj.y = self.PLAYER.y

        self.camera_obj.locked = [None, None]
        if flagged("!lock_X"):
            cam_lock_X = int(self.levelflags["!lock_X"])
            self.camera_obj.locked[0] = cam_lock_X

        if flagged("!lock_Y"):
            cam_lock_Y = int(self.levelflags["!lock_Y"])
            self.camera_obj.locked[1] = cam_lock_Y

        if flagged("!border_X"):
            cam_range_X = pyconfig.read_brackets(self.levelflags["!border_X"])
            self.camera_obj.border_x = [int(i) for i in cam_range_X[0].split(",")]

        if flagged("!border_Y"):
            cam_range_Y = pyconfig.read_brackets(self.levelflags["!border_Y"])
            self.camera_obj.border_y = [int(i) for i in cam_range_Y[0].split(",")]

    def add_sprite(self, new_sprite):
        new_sprite.add_default_attr(self)

        try:
            self.sprites[new_sprite.layer].append(new_sprite)
        except KeyError:
            self.sprites[new_sprite.layer] = [new_sprite]

    def purge_sprites(self, *layers):
        if not layers:
            for layer in self.sprites:
                self.sprites[layer] = []

        else:
            for l in layers:
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
        self.camera_obj.update_move(self)

        self.oncam_sprites = []
        for layer in self.sprites:
            for s in self.sprites[layer]:
                if self.camera_obj.on_camera(s) or s.persistent:
                    self.oncam_sprites.append(s)

        for cam_sprite in self.oncam_sprites:
            if cam_sprite.destroying:
                cam_sprite.update_destroy(self)
            else:
                cam_sprite.update_draw(self)

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
