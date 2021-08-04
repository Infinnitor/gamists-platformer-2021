import move_utils as move


class game_camera():
    def __init__(cam, pos, size):
        cam.x = pos[0]
        cam.y = pos[1]

        cam.w = size[0]
        cam.h = size[1]

        cam.camera_speed = 20

        x_collider_h = cam.w // 2
        y_collider_h = cam.h // 2

        cam.body = {
            "DOWN" : move.offset_rect(offset=(1, cam.h - y_collider_h), parent=cam, size=(cam.w - 2, y_collider_h)),
            "UP" : move.offset_rect(offset=(1, 0), parent=cam, size=(cam.w - 2, y_collider_h)),
            "LEFT" : move.offset_rect(offset=(0, 1), parent=cam, size=(x_collider_h, cam.h - 2)),
            "RIGHT" : move.offset_rect(offset=(cam.w - x_collider_h, 1), parent=cam, size=(x_collider_h, cam.h - 2))
        }

    def jump(self, pos):
        self.x = pos[0]
        self.y = pos[1]

    def update_move(cam, game):
        if game.sprites["PLAYER"]:
            p = game.sprites["PLAYER"][0]
            cam.camera_speed = abs(p.x_speed)
            if cam.camera_speed < 5:
                cam.camera_speed = 5
            p_x = p.x
            p_y = p.y
        else:
            p_x = game.win_w//2
            p_y = game.win_h//2

        target = (p_x - game.win_w//2, p_y - game.win_h//2)

        cam.x = move.value_to(value=cam.x, target=target[0], prox=20, step=cam.camera_speed)
        cam.update_collision(game, x=True)
        cam.y = move.value_to(value=cam.y, target=target[1], prox=20, step=cam.camera_speed)
        cam.update_collision(game, y=True)

    def update_collision(cam, game, x=False, y=False):

        cam_colliders = game.sprites["CAMERACOLLIDER"] + game.sprites["LEVELTRANSITION"]

        # Update collisions on X axis
        if x is True:

            # Update colliders
            cam.body["LEFT"].get_pos()
            cam.body["RIGHT"].get_pos()

            # Iterate through valid collision objects
            for t in cam_colliders:

                if move.rect_collision(cam.body["RIGHT"], t):

                    # Move player back based on the overlap between player right side and collider left side
                    depth = cam.x + cam.w - t.x
                    cam.x -= depth

                if move.rect_collision(cam.body["LEFT"], t):

                    # Move player back based on the overlap between player left side and collider right side
                    depth = t.x + t.w - cam.x
                    cam.x += depth

        # Update collisions on Y axis
        elif y is True:

            # Update colliders
            cam.body["DOWN"].get_pos()
            cam.body["UP"].get_pos()

            for t in cam_colliders:

                if move.rect_collision(cam.body["DOWN"], t):

                    # Move the player up based on overlap between player bottom and collider top
                    depth = cam.y + cam.h - t.y
                    cam.y -= depth

                if move.rect_collision(cam.body["UP"], t):
                    # Move the player back down based on overlap between collider bottom and player top
                    depth = t.y + t.h - cam.y
                    cam.y += depth

    def get_relative(cam, sprite):
        pass

    def on_camera(cam, sprite):
        if move.rect_collision(cam, sprite):
            return True
        return False

    def update_draw(cam, game):
        pass
