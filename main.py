from gameinfo import game_info, pygame, time, math, random
from sprite_class import sprite

import move_utils as move


def rect_collision(rect1, rect2):

    if rect1.x + rect1.w > rect2.x and rect1.x < rect2.x + rect2.w:
        if rect1.y + rect1.h > rect2.y and rect1.y < rect2.y + rect2.h:
            return True

    return False


def rect_collision_info(rect1, rect2):

    if rect1.x + rect1.w > rect2.x and rect1.x < rect2.x + rect2.w:
        if rect1.y + rect1.h > rect2.y and rect1.y < rect2.y + rect2.h:
            return True

    return False


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


class text_player():
    def __init__(self):
        file = text_clean(open("config.txt", "r"))

        values = {}
        for val in file:
            k, v = val.split(" : ")
            values[k] = float(v)

        self.x_acceleration = values["horizontal acceleration"]
        self.gravity = values["gravity"]
        self.terminal_velocity = values["vertical speed cap"]
        self.speed_cap = values["horizontal speed cap"]
        self.jump_str = values["jump strength"]
        self.held_jump_str = values["held jump strength"]
        self.held_jump_min = values["held jump min"]
        self.held_jump_max = values["held jump max"]

        self.x = values["start x"]
        self.y = values["start y"]
        self.w = values["player width"]
        self.h = values["player height"]


class text_level():
    def __init__(self):
        file = text_clean(open("mario 1-1.txt", "r"))

        self.terrain = []
        for val in file:
            line = val.split(" ")

            items = []
            for i in line:
                i = i.replace("(", "").replace(")", "")
                i = i.split(",")
                items.append([int(v) for v in i])

            self.terrain.append(items)


class player(sprite):
    layer = "PLAYER"

    def __init__(self, c):

        # Position
        self.x = c.x
        self.y = c.y

        # Width and height
        self.w = c.w
        self.h = c.h

        # Acceleration on the X axis
        self.x_acceleration = c.x_acceleration
        # Acceleration of gravity / downward acceleration on the Y axis
        self.gravity = c.gravity

        # The max force of gravity on the player
        self.terminal_velocity = c.terminal_velocity

        # The max speed that the player can move at on the X and Y axis
        self.speed_cap = c.speed_cap
        self.min_y_speed = self.terminal_velocity * -1

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

        # If the player is on the ground
        self.on_ground = False

        y_collider_h = self.terminal_velocity + 1
        x_collider_h = self.speed_cap
        # Player colliders
        self.colliders = {
            "DOWN" : move.offset_rect(offset=(1, self.h - y_collider_h), parent=self, size=(self.w - 2, y_collider_h)),
            "UP" : move.offset_rect(offset=(1, 0), parent=self, size=(self.w - 2, y_collider_h)),
            "LEFT" : move.offset_rect(offset=(0, 1), parent=self, size=(x_collider_h, self.h - 2)),
            "RIGHT" : move.offset_rect(offset=(self.w - x_collider_h, 1), parent=self, size=(x_collider_h, self.h - 2))
        }

    def update_move(self, game):

        # Move player based on left or right key press
        if game.check_key(pygame.K_LEFT, pygame.K_a):
            self.x_speed -= self.x_acceleration

            # If player is fighting against opposite momentum, move value closer to the inverse of current x_speed
            if self.x_speed > 0:
                self.x_speed = move.value_to(self.x_speed, self.x_speed * -1, step=self.x_acceleration, prox=0.5)

        elif game.check_key(pygame.K_RIGHT, pygame.K_d):
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
            if not self.on_ground:
                self.held_jump_frames = self.held_jump_max + 1

        # Add gravity to y_speed
        self.y_speed += self.gravity

        # Adjust so that downward momentum is never more than the terminal_velocity
        if self.y_speed > self.terminal_velocity:
            self.y_speed = self.terminal_velocity

        # If the upward momentum is more than the max, cap it
        if self.y_speed < self.min_y_speed:
            self.y_speed = self.min_y_speed

        # Move on X axis, then update X collision
        self.x += self.x_speed
        self.update_collision(game, x=True)
        # Move on Y axis, then update Y collision
        self.y += self.y_speed
        self.update_collision(game, y=True)

    def update_collision(self, game, x=False, y=False):

        # Update collisions on X axis
        if x is True:

            # Update colliders
            self.colliders["LEFT"].get_pos()
            self.colliders["RIGHT"].get_pos()

            # Iterate through valid collision objects
            for t in game.oncam_sprites:
                if t.layer != "TERRAIN":
                    continue

                if move.rect_collision(self.colliders["LEFT"], t):
                    # Freeze X momentum to halt the player
                    self.x_speed = 0

                    # Move player back based on the overlap between player left side and collider right side
                    depth = t.x + t.w - self.x
                    self.x += depth

                elif move.rect_collision(self.colliders["RIGHT"], t):
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

            # On ground will be False unless the DOWN collider has a successful collision
            self.on_ground = False
            for t in game.sprites["TERRAIN"]:
                if t.layer != "TERRAIN":
                    continue

                if move.rect_collision(self.colliders["DOWN"], t):

                    # If a collision occurs, on_ground is True and jump_frames are reset
                    self.on_ground = True
                    self.held_jump_frames = 0
                    self.y_speed = 0

                    # Move the player up based on overlap between player bottom and collider top
                    depth = self.y + self.h - t.y
                    self.y -= depth

                elif move.rect_collision(self.colliders["UP"], t):

                    # If a collision occurs on the UP collider, remove upward momentum
                    self.held_jump_frames = self.held_jump_max + 1
                    self.y_speed = 0

                    # Move the player back down based on overlap between collider bottom and player top
                    depth = t.y + t.h - self.y
                    self.y += depth

            # print(self.y_speed)

    def update_draw(self, game):
        # print(self)

        rel_x = self.x - game.camera_obj.x
        rel_y = self.y - game.camera_obj.y

        # Draw player and its colliders
        pygame.draw.rect(game.win, (155, 40, 40), (rel_x, rel_y, self.w, self.h))

        # for collider_rect in self.colliders.values():
        #     pygame.draw.rect(game.win, (255, 255, 255), collider_rect.get_pos())


class platform(sprite):
    layer = "TERRAIN"

    def __init__(self, pos, size, colour):
        self.x = pos[0]
        self.y = pos[1]

        self.w = size[0]
        self.h = size[1]

        self.colour = colour

    def update_draw(self, game):
        rel_x = self.x - game.camera_obj.x
        rel_y = self.y - game.camera_obj.y

        pygame.draw.rect(game.win, self.colour, (rel_x, rel_y, self.w, self.h))


def mainloop(game, player_config, level_config):
    game.add_sprite(player(player_config))

    for pos, size, colour in level_config.terrain:
        game.add_sprite(platform(pos=pos, size=size, colour=colour))

    while game.run:
        game.update_keys()
        game.update_draw()

        game.update_scaled()
        game.update_state()

        if game.check_key(pygame.K_r, buffer=True):
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


while True:
    player_config = text_player()
    level_config = text_level()
    if mainloop(game, player_config, level_config):
        game.purge_sprites()
    else:
        break
