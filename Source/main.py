from gameinfo import game_info, pygame, time, math, random
from colour_manager import colours

from sprite_class import sprite

import move_utils as move
import draw_utils as drawu

import pyconfig as config

import asset


def rect_collision(rect1, rect2):

    if rect1.x + rect1.w > rect2.x and rect1.x < rect2.x + rect2.w:
        if rect1.y + rect1.h > rect2.y and rect1.y < rect2.y + rect2.h:
            return True

    return False


class deadplayer(sprite):
    layer = "LOWPARTICLE"

    def __init__(self, player, sink_depth, sink_speed):
        self.x = player.x
        self.y = player.y

        self.w = player.w
        self.h = player.h

        self.c = player.c

        self.start_y = self.y
        self.sink_depth = sink_depth
        self.sink_speed = sink_speed

    def update_move(self, game):
        self.y += self.sink_speed

    def update_draw(self, game):
        rel_x = self.x - game.camera_obj.x
        rel_y = self.y - game.camera_obj.y

        # Draw player and its colliders
        pygame.draw.rect(game.win, self.c, (rel_x, rel_y, self.w, self.h))

    def sunk(self):
        if self.y > self.start_y + self.sink_depth:
            self.kill()
            return True
        return False


# Player physics info
class physics_info():
    def __init__(self):
        self.on_ground = False

        self.walljump = False
        self.head_hit = False

        self.left = False
        self.right = False

    def turn_left(self):
        self.right = False
        self.left = True

    def turn_right(self):
        self.left = False
        self.right = True

    def air_reset(self):
        self.on_ground = False
        self.walljump = False
        self.head_hit = False


class player(sprite):
    layer = "PLAYER"
    persistent = True

    def __init__(self, c):

        # Position
        self.x = c.x
        self.y = c.y

        # Width and height
        self.w = c.w
        self.h = c.h

        self.c = colours.red

        # Acceleration on the X axis
        self.x_acceleration = c.x_acceleration
        # Acceleration of gravity / downward acceleration on the Y axis
        self.gravity = c.gravity

        # The max force of gravity on the player
        self.terminal_velocity = c.terminal_velocity

        # The max speed that the player can move at on the X and Y axis
        self.speed_cap = c.speed_cap
        self.min_y_speed = self.terminal_velocity * -1

        if self.terminal_velocity > self.speed_cap:
            self.collision_order = False
        else:
            self.collision_order = True

        # Player momentum on both the X and Y
        self.x_speed = 0
        self.y_speed = 0

        # Upward acceleration when jumping
        self.jump_str = c.jump_str
        self.held_jump_str = c.held_jump_str

        # The number of frames that the player has been jumping
        self.held_jump_frames = 0
        self.held_jump_min = c.held_jump_min
        self.held_jump_max = c.held_jump_max

        self.PHYS = physics_info()

        y_collider_h = self.terminal_velocity + 1
        x_collider_h = self.speed_cap
        # Player colliders
        self.colliders = {
            "DOWN" : move.offset_rect(offset=(1, self.h - y_collider_h), parent=self, size=(self.w - 2, y_collider_h)),
            "UP" : move.offset_rect(offset=(1, 0), parent=self, size=(self.w - 2, y_collider_h)),
            "LEFT" : move.offset_rect(offset=(0, 1), parent=self, size=(x_collider_h, self.h - 2)),
            "RIGHT" : move.offset_rect(offset=(self.w - x_collider_h, 1), parent=self, size=(x_collider_h, self.h - 2))
        }

        self.set_spawn((self.x, self.y))
        self.dead_player = None

    def set_spawn(self, pos):
        self.spawnpos = pos

    def respawn(self, halt=True, boost_y=0):
        if halt is True:
            self.x_speed = 0
            self.y_speed = 0

        self.y_speed -= boost_y

        self.x = self.spawnpos[0]
        self.y = self.spawnpos[1]

    def update_move(self, game):
        if game.check_key(pygame.K_r, buffer=True):
            self.respawn()

        # Move player based on left or right key press
        if game.check_key(pygame.K_LEFT, pygame.K_a):
            self.PHYS.turn_left()

            self.x_speed -= self.x_acceleration

            # If player is fighting against opposite momentum, move value closer to the inverse of current x_speed
            if self.x_speed > 0:
                self.x_speed = move.value_to(self.x_speed, self.x_speed * -1, step=self.x_acceleration, prox=0.5)

        elif game.check_key(pygame.K_RIGHT, pygame.K_d):
            self.PHYS.turn_left()

            self.x_speed += self.x_acceleration
            if self.x_speed < 0:
                self.x_speed = move.value_to(self.x_speed, self.x_speed * -1, step=self.x_acceleration, prox=0.5)

        # Slow player down if left or right are not pre
        else:
            self.x_speed = move.value_to(self.x_speed, 0, step=self.x_acceleration, prox=0.5)

        # Adjust x_speed if it is above the max momentum cap on the X axis
        if self.x_speed > self.speed_cap:
            self.x_speed = self.speed_cap

        elif self.x_speed < self.speed_cap * -1:
            self.x_speed = self.speed_cap * -1

        # If presses space, add vertical momentum
        if game.check_key(pygame.K_SPACE, pygame.K_UP):

            # Stop further additions to upward momentum if the player has hit the max height
            if self.held_jump_frames <= self.held_jump_max:

                # Allow for jumping if the player is within the correct window of frames
                if self.held_jump_frames == 0:
                    self.y_speed -= self.jump_str
                elif self.held_jump_frames >= self.held_jump_min:
                    self.y_speed -= self.held_jump_str

            # Increment by one
            self.held_jump_frames += 1
        else:

            # If pressing of space is broken, prevent further upward momentum increments
            if not self.PHYS.on_ground:
                self.held_jump_frames = self.held_jump_max + 1

        # Add gravity to y_speed
        self.y_speed += self.gravity

        # Adjust so that downward momentum is never more than the terminal_velocity
        if self.y_speed > self.terminal_velocity:
            self.y_speed = self.terminal_velocity

        # If the upward momentum is more than the max, cap it
        if self.y_speed < self.min_y_speed:
            self.y_speed = self.min_y_speed

        if self.collision_order:
            # Move on X axis, then update X collision
            self.x += self.x_speed
            self.update_collision(game, x=True)
            # Move on Y axis, then update Y collision
            self.y += self.y_speed
            self.update_collision(game, y=True)

        else:
            self.y += self.y_speed
            self.update_collision(game, y=True)
            self.x += self.x_speed
            self.update_collision(game, x=True)

    def update_collision(self, game, x=False, y=False):

        # Update collisions on X axis
        if x is True:

            # Update colliders
            self.colliders["LEFT"].get_pos()
            self.colliders["RIGHT"].get_pos()

            # Iterate through valid collision objects
            for t in game.oncam_sprites:

                if t.layer == "CHECKPOINTS":
                    if t.collide(self):
                        self.set_spawn((t.x, t.y))

                if t.layer == "HAZARD":
                    t.collide(self)

                if t.layer == "LEVELTRANSITION":
                    t.collide(self)

                if t.layer != "TERRAIN":
                    continue

                if t.collide(self.colliders["LEFT"]):
                    # Freeze X momentum to halt the player
                    self.x_speed = 0

                    # Move player back based on the overlap between player left side and collider right side
                    depth = t.x + t.w - self.x
                    self.x += depth

                elif t.collide(self.colliders["RIGHT"]):
                    # Freeze X momentum
                    self.x_speed = 0

                    # Move player back based on the overlap between player right side and collider left side
                    depth = self.x + self.w - t.x
                    self.x -= depth

        # Update collisions on Y axis
        elif y is True:

            # Update colliders
            self.colliders["DOWN"].get_pos()
            self.colliders["UP"].get_pos()

            self.PHYS.air_reset()
            for t in game.oncam_sprites:

                if t.layer != "TERRAIN":
                    continue

                if t.collide(self.colliders["DOWN"]):

                    # If a collision occurs, on_ground is True and jump_frames are reset
                    self.PHYS.on_ground = True
                    self.held_jump_frames = 0
                    self.y_speed = 0

                    # Move the player up based on overlap between player bottom and collider top
                    depth = self.y + self.h - t.y
                    self.y -= depth

                if t.collide(self.colliders["UP"]):

                    # If a collision occurs on the UP collider, remove upward momentum
                    self.held_jump_frames = self.held_jump_max + 1
                    self.y_speed = 0

                    # Move the player back down based on overlap between collider bottom and player top
                    depth = t.y + t.h - self.y
                    self.y += depth

                    if not self.PHYS.on_ground:
                        self.PHYS.head_hit = True
                        drawu.particles.explosion(number=20, pos=(self.x + self.w//2, self.y + self.h//2), speed=2, colour=(155, 35, 35), lifetime=60, game=game)

    def update_draw(self, game):
        # print(self)

        rel_x = self.x - game.camera_obj.x
        rel_y = self.y - game.camera_obj.y

        # Draw player and its colliders
        pygame.draw.rect(game.win, self.c, (rel_x, rel_y, self.w, self.h))

        # for collider_rect in self.colliders.values():
        #     pygame.draw.rect(game.win, (255, 255, 255), collider_rect.get_pos())

    def update_destroy(self, game):
        if self.dead_player is None:
            self.dead_player = deadplayer(self, 60, 1)
            game.add_sprite(self.dead_player)
        else:

            if self.dead_player.sunk():
                self.respawn()
                self.destroying = False
                self.dead_player = None


def mainloop(game):
    game.add_sprite(player(config.player))
    game.load_level('cave1.txt')

    while game.run:
        game.update_keys()
        game.update_draw()

        game.update_scaled()
        game.update_state()

        if game.check_key(pygame.K_q, buffer=True):
            return True

    return False


game = game_info(
                name="the mario killer",
                win_w=1280,
                win_h=720,
                user_w=1920,
                user_h=1080,
                bg=(0, 0, 0),
                framecap=60,
                show_framerate=False,
                quit_key=pygame.K_ESCAPE)

# Asset must be initialised after game sets the display surface
asset.init()


while True:
    if mainloop(game):
        game.purge_sprites()
    else:
        break
