from gameinfo import game_info, pygame, time, math, random

from colour_manager import colours
from sprite_class import sprite

import move_utils as move
import draw_utils as drawu

import particles

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

        self.death_transition = None
        self.frametick = None
        self.surface = None

    def update_move(self, game):
        if self.frametick is None:
            self.frametick = move.frametick(15, game)
            game.init_screenshake(15, 5, rand=True)

        if self.death_transition is None and self.frametick.get():
            self.death_transition = drawu.bubblewipe(direction="DOWN", num_bubbles=9, tick=1, colour=colours.red, randspeed=True, randcol=True, game=game)
            game.add_sprite(self.death_transition)

        if self.surface is None:
            self.surface = game.PLAYER.surface

        self.y += self.sink_speed

    def update_draw(self, game):
        rel_x = self.x - game.camera_obj.x
        rel_y = self.y - game.camera_obj.y

        # Draw player and its colliders
        # pygame.draw.rect(game.win, self.c, (rel_x, rel_y, self.w, self.h))
        game.win.blit(self.surface, (rel_x, rel_y))

    def sunk(self):
        if self.death_transition is not None:
            if self.death_transition.blocking:
                self.kill()
                return True
        return False


class pogo(sprite):
    layer = "PLAYER"

    def __init__(self, player, pos, size, force_vel, lifetime):
        self.p = player
        self.p.PHYS.pogo_active = True

        self.x = pos[0]
        self.y = pos[1]

        self.w = size[0]
        self.h = size[1]

        self.force = force_vel
        self.collide_sprites = ("POGO", "TERRAIN", "HAZARD")

        self.lifetime = lifetime

    def follow_player(self):
        self.x = self.p.x
        self.y = self.p.y

    def update_move(self, game):
        self.lifetime -= 1
        if self.lifetime < 1:
            self.p.PHYS.pogo_active = False
            self.kill()

        self.follow_player()

        colliders = []
        [colliders.extend(game.sprites[k]) for k in self.collide_sprites]

        for s in colliders:
            if move.rect_collision(self, s):
                self.p.PHYS.add_force(self.force, ticks=3)

                self.p.PHYS.refresh_jump()
                self.p.PHYS.grounded()

                self.p.PHYS.pogo_active = False
                self.destroying = True

    def update_draw(self, game):
        rel_x = self.x - game.camera_obj.x
        rel_y = self.y - game.camera_obj.y

        pygame.draw.rect(game.win, colours.black, (rel_x + 10, rel_y, self.w - 20, self.h))

    def update_destroy(self, game):
        self.lifetime -= 1
        if self.lifetime < 1:
            self.p.PHYS.pogo_active = False
            self.kill()

        self.follow_player()
        self.update_draw(game)


# Player physics info
class physics_info():
    class timed_force():
        def __init__(f, vel, ticks):
            f.x_add = vel[0]
            f.y_add = vel[1]

            f.tick_len = ticks
            f.tick = 0

        def __repr__(f):
            return f"Force: ({f.x_add}, {f.y_add}) Time: {f.tick_len}"

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

        self.pogo_active = False
        self.dash = False

        self.head_hit = False
        self.ground_hit = False

        # One has to be True by default lol
        self.left = False
        self.right = True

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

        self.p.dashes = self.p.num_dashes

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
        self.x = c.start_x
        self.y = c.start_y

        # Width and height
        self.w = c.player_width
        self.h = c.player_height

        self.c = colours.red

        # Acceleration on the X axis
        self.x_acceleration = c.horizontal_acceleration
        # Acceleration of gravity / downward acceleration on the Y axis
        self.gravity = c.gravity

        # The max force of gravity on the player
        self.terminal_velocity = c.vertical_speed_cap

        # The max speed that the player can move at on the X and Y axis
        self.speed_cap = c.horizontal_speed_cap
        self.min_y_speed = self.terminal_velocity * -1

        if self.terminal_velocity > self.speed_cap:
            self.collision_order = False
        else:
            self.collision_order = True

        self.wallslide_speed = c.wallslide_speed
        self.walljump_window = c.walljump_frames
        self.walljump_str = c.walljump_strength

        # Player momentum on both the X and Y
        self.x_speed = 0
        self.y_speed = 0

        # Upward acceleration when jumping
        self.jump_str = c.jump_strength
        self.held_jump_str = c.held_jump_strength

        # The number of frames that the player has been jumping
        self.held_jump_frames = 0
        self.held_jump_min = c.held_jump_min
        self.held_jump_max = c.held_jump_max

        self.num_dashes = c.dashes_number
        self.dashes = c.dashes_number
        self.dash_str = c.dash_strength

        self.dash_length = c.dash_length
        self.dashing_frames = 0

        self.num_jumps = c.jumps_number
        self.jumps = c.jumps_number

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

        self.surface = pygame.Surface((self.w, self.h))
        self.surface.blit(asset.TEXTURE.platform_map, (0, 0, self.w, self.h))

    def set_spawn(self, pos):
        self.spawnpos = pos

    def respawn(self, halt=True, boost_y=0):
        if halt is True:
            self.x_speed = 0
            self.y_speed = 0
            self.PHYS.forces = []

        self.y_speed -= boost_y

        self.x = self.spawnpos[0]
        self.y = self.spawnpos[1]

    def update_move(self, game):

        if self.PHYS.freeze is True:
            return

        if game.check_key(pygame.K_r, buffer=True):
            self.destroying = True

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
                    self.x_speed = self.walljump_str
                    self.PHYS.add_force((self.x_acceleration * 2, 0), 10)
                    self.PHYS.walljump_frames = 0

                elif self.PHYS.walljump_right:
                    self.x_speed = self.walljump_str * -1
                    self.PHYS.add_force((self.x_acceleration * -2, 0), 10)
                    self.PHYS.walljump_frames = 0

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

        if game.check_key(pygame.K_DOWN, buffer=True) and self.PHYS.pogo_active is False and self.PHYS.on_ground is False:
            p = pogo(self, (self.x, self.y), (self.w, self.h*4), (0, -10), 25)
            game.add_sprite(p)

        if game.check_key(pygame.K_LSHIFT, buffer=True) and self.PHYS.dash is False:

            if self.dashes > 0:
                self.dashes -= 1

                self.dashing_frames = self.dash_length
                game.init_screenshake(8, 6, rand=True, spread=(0.8, 1.2))

                if self.PHYS.left is True:
                    dashforce = (self.dash_str * -1, 0)
                elif self.PHYS.right is True:
                    dashforce = (self.dash_str, 0)

                self.PHYS.add_force(dashforce, self.dash_length)

            else:
                game.init_screenshake(2, 4)

        if self.dashing_frames > 0:
            self.PHYS.dash = True
        else:
            self.PHYS.dash = False

        if self.PHYS.dash is True:
            self.dashing_frames -= 1
            self.y_speed = 0
        else:
            # Gravity does not come into effect when dashing
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

                if t.layer in ("HAZARD", "POGO", "LEVELTRANSITION", "CAMERACOLLIDER"):
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
            game.particles.explosion(
                                        particles.circle, (self.x + self.w//2, self.y), 10,
                                        size=12,
                                        speed=3,
                                        colour=(3, 3, 3),
                                        randspeed=1,
                                        randcol=3,
                                        layer="LOWPARTICLE"
                                    )

        if self.PHYS.ground_hit:
            game.particles.explosion(particles.circle, (self.x + self.w//2, self.y + self.h), 10, size=12, speed=3, colour=(3, 3, 3), lifetime=25, randspeed=1, randcol=3, layer="LOWPARTICLE")

        if self.PHYS.dash:

            a_range = (-90, 90)
            if self.PHYS.left:
                a_range = (90, 270)

            # game.particles.explosion(particles.circle, 5, (self.x + self.w//2, random.randint(int(self.y), int(self.y + self.h))), size=12, speed=1, colour=(6, 6, 6), lifetime=25, randspeed=1, randcol=2, layer="LOWPARTICLE")
            game.particles.cone(
                                        particles.diamond, (self.x + self.w//2, random.randint(int(self.y), int(self.y + self.h))), 10,
                                        a_range,
                                        size=25,
                                        speed=3,
                                        colour=(3, 3, 3),
                                        randcol=1,
                                        randspeed=1,
                                        layer="LOWPARTICLE"
                                    )

        rel_x = self.x - game.camera_obj.x
        rel_y = self.y - game.camera_obj.y

        # Draw player and its colliders
        # pygame.draw.rect(game.win, c, (rel_x, rel_y, self.w, self.h))
        game.win.blit(self.surface, (rel_x, rel_y))

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
    game.PLAYER = game.sprites["PLAYER"][0]

    game.load_level('center.txt', player_spawn=bool(config.player.auto_spawn))

    show_player_attr = False
    while game.run:
        game.update_keys()

        if game.check_key(pygame.K_0):
            game.add_text(game.PLAYER)

        if game.check_key(pygame.K_F1, buffer=True):
            game.show_framerate = not game.show_framerate

        if game.check_key(pygame.K_F3, buffer=True):
            show_player_attr = not show_player_attr

        if show_player_attr is True:
            game.add_text(f'X: {round(game.PLAYER.x)} Y: {round(game.PLAYER.y)}')
            for a in game.PLAYER.PHYS.__dict__:
                if a == "p":
                    continue

                game.add_text(f"{a} : {game.PLAYER.PHYS.__dict__[a]}")

        game.update_draw()

        game.update_scaled()
        game.update_state()

        if game.check_key(pygame.K_q, buffer=True):
            game.purge_sprites()
            config.load()
            mainloop(game)


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
mainloop(game)
