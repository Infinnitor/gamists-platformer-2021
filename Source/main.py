from gameinfo import game_info, pygame, time, math, random
from colour_manager import colours

from sprite_class import sprite

import move_utils as move
import draw_utils as drawu

import particles
import particles_shortcuts as part_shortcuts

import pyconfig as config

import asset


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
    class timed_force():
        def __init__(f, vel, ticks):
            f.x_add = vel[0]
            f.y_add = vel[1]

            f.tick_len = ticks
            f.tick = 0

        def update(f, obj):
            obj.x_speed += f.x_add
            obj.y_speed += f.y_add

            f.tick += 1
            if f.tick >= f.tick_len:
                return False

            return True

    def __init__(self, player):
        self.p = player

        self.freeze = False

        self.on_ground = False

        self.walljump = False
        self.walljump_frames = 0
        self.walljump_left = True
        self.walljump_right = False

        self.head_hit = False
        self.ground_hit = False

        self.left = False
        self.right = False

        self.can_jump = False

        self.coyote_time = 0

        self.forces = []

    def add_force(self, vel, ticks=1):
        self.forces.append(self.timed_force(vel, ticks))

    def turn_left(self):
        self.right = False
        self.left = True

    def turn_right(self):
        self.left = False
        self.right = True

    # These ones are actually important
    def air_reset(self):
        self.head_hit = False
        self.ground_hit = False

        self.walljump = False
        self.walljump_frames -= 1
        if self.walljump_frames < 0:
            self.walljump_frames = 0

        self.on_ground = False
        self.can_jump = False

    def grounded(self):
        self.on_ground = True
        self.can_jump = True

        self.p.held_jump_frames = 0
        self.p.jumps = self.p.num_jumps

        if self.p.y_speed > self.p.gravity * 2:
            self.ground_hit = True
        else:
            self.ground_hit = False

        self.refresh_jump()

    def refresh_jump(self):
        self.can_jump = True
        self.p.held_jump_frames = 0

        self.p.y_speed = 0

    def refresh_walljump(self):
        self.walljump = True
        self.walljump_frames = 10

        if self.left is True:
            self.walljump_right = False
            self.walljump_left = True
        else:
            self.walljump_left = False
            self.walljump_right = True

    def update_move(self):
        valid_forces = []
        for f in self.forces:
            if f.update(self.p):
                valid_forces.append(f)

        self.forces = valid_forces


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

        self.wallslide_speed = c.wallslide_speed
        self.walljump_window = c.walljump_window

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

        self.dashing_frames = 0

        self.num_jumps = c.jumps
        self.jumps = c.jumps

        self.PHYS = physics_info(self)

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

        if self.PHYS.freeze is True:
            return

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
            self.PHYS.turn_right()

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

            if self.PHYS.walljump_frames > 0 and game.check_key(pygame.K_SPACE, pygame.K_UP, buffer=True):
                self.PHYS.grounded()

                if self.PHYS.walljump_left:
                    self.x_speed = 9
                    self.PHYS.add_force((self.x_acceleration * 2, 0), 10)

                elif self.PHYS.walljump_right:
                    self.x_speed = -9
                    self.PHYS.add_force((self.x_acceleration * -2, 0), 10)

            if self.jumps > 0:
                if game.check_key(pygame.K_SPACE, pygame.K_UP, buffer=True) or self.PHYS.on_ground: # Little fix here btw not sure if it causes any other problems

                    self.jumps -= 1
                    self.PHYS.refresh_jump()

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
            if not self.PHYS.can_jump:
                self.held_jump_frames = self.held_jump_max + 1

        if game.check_key(pygame.K_LSHIFT, buffer=True):
            self.dashing_frames = 15
            game.init_screenshake(8, 6, rand=True, spread=(0.8, 1.2))

            if self.PHYS.left is True:
                dashforce = (self.speed_cap * -1, 0)
            elif self.PHYS.right is True:
                dashforce = (self.speed_cap, 0)

            self.PHYS.add_force(dashforce, 15)

        if self.dashing_frames > 0:
            self.dashing_frames -= 1
            self.y_speed = 0
        else:
            # Add gravity to y_speed
            self.y_speed += self.gravity

        # Adjust so that downward momentum is never more than the terminal_velocity
        if self.y_speed > self.terminal_velocity:
            self.y_speed = self.terminal_velocity

        # If the upward momentum is more than the max, cap it
        if self.y_speed < self.min_y_speed:
            self.y_speed = self.min_y_speed

        if self.PHYS.walljump and self.y_speed > self.wallslide_speed:
            self.y_speed = self.wallslide_speed

        # Update other forces that may be acting on the player
        self.PHYS.update_move()

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

                    if not self.PHYS.on_ground:
                        self.PHYS.refresh_walljump()

                    # Move player back based on the overlap between player left side and collider right side
                    depth = t.x + t.w - self.x
                    self.x += depth

                if t.collide(self.colliders["RIGHT"]):
                    # Freeze X momentum
                    self.x_speed = 0

                    if not self.PHYS.on_ground:
                        self.PHYS.refresh_walljump()

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
                    self.PHYS.grounded()
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

    def update_draw(self, game):

        # Effects stuff first
        if self.PHYS.head_hit:
            game.init_screenshake(4, 4)
            part = particles.TEMPLATES.circle.modify(size=12, speed=3, colour=(255, 124, 0), lifetime=30)
            part_shortcuts.explosion(10, (self.x + self.w//2, self.y), part, layer="LOWPARTICLE", game=game)

        if self.PHYS.ground_hit:
            part = particles.TEMPLATES.circle.modify(size=12, speed=3, colour=(255, 124, 0), lifetime=30)
            part_shortcuts.explosion(20, (self.x + self.w//2, self.y + self.h), part, layer="HIGHPARTICLE", game=game)

        cols = ((35, 35, 155), (35, 155, 35), (155, 35, 35))
        # if self.PHYS.walljump_frames > 0:
        #     c = (0, 255, 0)

        c = cols[int(self.jumps)]
        if self.dashing_frames:
            part = particles.TEMPLATES.circle.modify(size=10, speed=3, colour=c, lifetime=15)
            part_shortcuts.explosion(5, (self.x + self.w//2, random.randint(int(self.y), int(self.y + self.h))), part, layer="LOWPARTICLE", game=game)

        rel_x = self.x - game.camera_obj.x
        rel_y = self.y - game.camera_obj.y

        # Draw player and its colliders
        pygame.draw.rect(game.win, c, (rel_x, rel_y, self.w, self.h))

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
    game.load_level('room1.txt')

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
                user_w=1280,
                user_h=720,
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
