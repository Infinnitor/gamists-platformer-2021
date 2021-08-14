import move_utils as move


class game_camera():
    def __init__(self, pos, size):
        self.x = pos[0]
        self.y = pos[1]

        self.w = size[0]
        self.h = size[1]

        self.camera_speed = 20

        self.locked = False

        x_collider_h = self.w // 2
        y_collider_h = self.h // 2

        self.body = {
            "DOWN" : move.offset_rect(offset=(1, self.h - y_collider_h), parent=self, size=(self.w - 2, y_collider_h)),
            "UP" : move.offset_rect(offset=(1, 0), parent=self, size=(self.w - 2, y_collider_h)),
            "LEFT" : move.offset_rect(offset=(0, 1), parent=self, size=(x_collider_h, self.h - 2)),
            "RIGHT" : move.offset_rect(offset=(self.w - x_collider_h, 1), parent=self, size=(x_collider_h, self.h - 2))
        }

    def jump(self, pos):
        self.x = pos[0]
        self.y = pos[1]

    def update_move(self, game):
        if self.locked is not False:
            self.x = self.locked[0]
            self.y = self.locked[1]

        if game.sprites["PLAYER"]:
            p = game.sprites["PLAYER"][0]
            self.camera_speed = abs(p.x_speed)
            if self.camera_speed < 5:
                self.camera_speed = 5
            p_x = p.x
            p_y = p.y
        else:
            p_x = game.win_w//2
            p_y = game.win_h//2

        player_pos = (p_x - game.win_w//2, p_y - game.win_h//2)

        self.x = player_pos[0]
        self.update_collision(game, x=True)
        self.y = player_pos[1]
        self.update_collision(game, y=True)

    def update_collision(self, game, x=False, y=False):

        cam_colliders = game.sprites["CAMERACOLLIDER"] + game.sprites["LEVELTRANSITION"]

        # Update collisions on X axis
        if x is True:

            # Update colliders
            self.body["LEFT"].get_pos()
            self.body["RIGHT"].get_pos()

            # Iterate through valid collision objects
            for t in cam_colliders:

                if move.rect_collision(self.body["RIGHT"], t):

                    # Move player back based on the overlap between player right side and collider left side
                    depth = self.x + self.w - t.x
                    self.x -= depth

                if move.rect_collision(self.body["LEFT"], t):

                    # Move player back based on the overlap between player left side and collider right side
                    depth = t.x + t.w - self.x
                    self.x += depth

        # Update collisions on Y axis
        elif y is True:

            # Update colliders
            self.body["DOWN"].get_pos()
            self.body["UP"].get_pos()

            for t in cam_colliders:

                if move.rect_collision(self.body["DOWN"], t):

                    # Move the player up based on overlap between player bottom and collider top
                    depth = self.y + self.h - t.y
                    self.y -= depth

                if move.rect_collision(self.body["UP"], t):
                    # Move the player back down based on overlap between collider bottom and player top
                    depth = t.y + t.h - self.y
                    self.y += depth

    def get_relative(self, sprite):
        pass

    def on_camera(self, sprite):
        if move.rect_collision(self, sprite):
            return True
        return False

    def update_draw(self, game):
        pass
