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


class player(sprite):
    layer = "PLAYER"

    def __init__(self, pos, size, speed):

        # Position
        self.x = pos[0]
        self.y = pos[1]

        # Width and height
        self.w = size[0]
        self.h = size[1]

        # Acceleration on the X axis
        self.x_acceleration = speed[0]
        # Acceleration of gravity / downward acceleration on the Y axis
        self.gravity = speed[1]

        # The max force of gravity on the player
        self.terminal_velocity = 11

        # The max speed that the player can move at on the X and Y axis
        self.speed_cap = 7
        self.min_y_speed = self.terminal_velocity * -1

        # Player momentum on both the X and Y
        self.x_speed = 0
        self.y_speed = 0

        # Upward acceleration when jumping
        self.jump_str = 20

        # The number of frames that the player has been jumping
        self.held_jump_frames = 0
        self.held_jump_min = 5
        self.held_jump_max = 10

        # If the player is on the ground
        self.on_ground = False

        collider_h = 1
        # Player colliders
        self.colliders = {
            "DOWN" : move.offset_rect(offset=(1, self.h - collider_h), parent=self, size=(self.w - 2, collider_h)),
            "UP" : move.offset_rect(offset=(1, 0), parent=self, size=(self.w - 2, collider_h)),
            "LEFT" : move.offset_rect(offset=(0, 1), parent=self, size=(collider_h, self.h - 2)),
            "RIGHT" : move.offset_rect(offset=(self.w, 1), parent=self, size=(collider_h, self.h - 2))
        }

    def update_move(self, game):

        # Move player based on left or right key press
        if game.check_key(pygame.K_LEFT, pygame.K_a):
            self.x_speed -= self.x_acceleration

            # If player is fighting against opposite momentum, move value closer to the inverse of current x_speed
            if self.x_speed > 0:
                self.x_speed = move.value_to(self.x_speed, self.x_speed * -1, step=1, prox=0.5)

        elif game.check_key(pygame.K_RIGHT, pygame.K_d):
            self.x_speed += self.x_acceleration
            if self.x_speed < 0:
                self.x_speed = move.value_to(self.x_speed, self.x_speed * -1, step=1, prox=0.5)

        # Slow player down if left or right are not pre
        else:
            self.x_speed = move.value_to(self.x_speed, 0, step=1, prox=0.5)

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
                if self.held_jump_frames >= self.held_jump_min or self.held_jump_frames == 0:
                    self.y_speed -= self.jump_str

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
        self.update_collision(game, "X")
        # Move on Y axis, then update Y collision
        self.y += self.y_speed
        self.update_collision(game, "Y")

    def update_collision(self, game, axis):

        # Update collisions on X axis
        if axis == "X":

            # Update colliders
            self.colliders["LEFT"].get_pos()
            self.colliders["RIGHT"].get_pos()

            # Iterate through valid collision objects
            for t in game.sprites["TERRAIN"]:

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
        elif axis == "Y":

            # Update colliders
            self.colliders["DOWN"].get_pos()
            self.colliders["UP"].get_pos()

            # On ground will be False unless the DOWN collider has a successful collision
            self.on_ground = False
            for t in game.sprites["TERRAIN"]:
                if move.rect_collision(self.colliders["DOWN"], t):

                    # If a collision occurs, on_ground is True and jump_frames are reset
                    self.on_ground = True
                    self.held_jump_frames = 0

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
            print(self.y_speed)

    def update_draw(self, game):

        # Draw player and its colliders
        pygame.draw.rect(game.win, (155, 40, 40), (self.x, self.y, self.w, self.h))
        for collider_rect in self.colliders.values():
            pygame.draw.rect(game.win, (255, 255, 255), collider_rect.get_pos())


class platform(sprite):
    layer = "TERRAIN"

    def __init__(self, pos, size, colour):
        self.x = pos[0]
        self.y = pos[1]

        self.w = size[0]
        self.h = size[1]

        self.colour = colour

    def update_draw(self, game):
        pygame.draw.rect(game.win, self.colour, (self.x, self.y, self.w, self.h))


def mainloop(game):
    game.add_sprite(player(pos=(500, 500), size=(50, 50), speed=(1, 0.5)))
    game.add_sprite(platform(pos=(0, 600), size=(1280, 200), colour=(35, 35, 155)))
    game.add_sprite(platform(pos=(300, 350), size=(700, 50), colour=(49, 52, 63)))
    game.add_sprite(platform(pos=(0, 550), size=(700, 100), colour=(49, 52, 63)))

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
    if mainloop(game):
        game.purge_sprites()
    else:
        break
