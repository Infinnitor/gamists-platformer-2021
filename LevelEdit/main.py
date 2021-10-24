from gameinfo import game_info, pygame, math, random, gameloop
from sprite_class import sprite
import pickle


class camera(sprite):

    layer = "CAMERA"

    def __init__(self, start_pos, size):
        self.x = start_pos[0]
        self.y = start_pos[1]

        self.w = size[0]
        self.h = size[1]

        self.speed = 10

    def update_move(self, game):
        if game.check_key(pygame.K_a):
            self.x -= self.speed
        if game.check_key(pygame.K_d):
            self.x += self.speed

        if game.check_key(pygame.K_w):
            self.y -= self.speed
        if game.check_key(pygame.K_s):
            self.y += self.speed

    def get_rel(self, sprite):
        return sprite.x - self.x, sprite.y - self.y


class button(sprite):
    layer = "UI"

    def __init__(self, pos, size, function, args):
        self.x = pos[0]
        self.y = pos[1]

        self.w = size[0]
        self.h = size[1]

        self.FUNC = function
        self.args = args

    def selected(self, game):
        if not game.check_mouse(0, buffer=True):
            return

        if game.mouse_pos[0] > self.x and game.mouse_pos[0] < self.x + self.w:
            if game.mouse_pos[1] > self.y and game.mouse_pos[1] < self.y + self.h:
                return True
        return False

    def update_move(self, game):
        if self.selected(game):
            self.FUNC(*self.args)

    def update_draw(self, game):
        pygame.draw.rect(game.win, (0, 0, 0), (self.x, self.y, self.w, self.h))


class toolbar(sprite):
    layer = "UI"

    c = (95, 95, 95)

    def __init__(self, pos, size, game):
        self.x = pos[0]
        self.y = pos[1]

        self.w = size[0]
        self.h = size[1]

        def spawn_block(game):
            new_sprite = test_element((800, 400), (100, 100))
            game.add_sprite(new_sprite)
            new_sprite.context_menu(game)
            new_sprite.clicked = True
            game.current_selected_element = new_sprite

        self.TABS = {
            "TERRAIN" : [button((self.x + 20, self.y + 120), (self.w - 40, 80), spawn_block, [game])]
        }

        self.current_tab = "TERRAIN"

    def update_move(self, game):
        for button in self.TABS[self.current_tab]:
            button.update_move(game)

    def update_draw(self, game):
        pygame.draw.rect(game.win, self.c, (self.x, self.y, self.w, self.h))
        for button in self.TABS[self.current_tab]:
            button.update_draw(game)


class camera_sprite(sprite):

    layer = "TERRAIN"

    def update_move(self, game):
        self.rel_x, self.rel_y = game.CAMERA.get_rel(self)

        if self.selected(game):
            if self.clicked is True:
                self.clicked = False
                game.current_selected_element = None
            else:
                self.clicked = True
                game.current_selected_element = self

        if self.clicked:
            self.context_menu(game)
            if game.current_selected_element is not None:
                if game.current_selected_element is not self:
                    self.clicked = False

        else:
            self.moving = False
            self.resizing = False

        if self.moving:
            self.x = game.mouse_pos[0] + game.CAMERA.x
            self.y = game.mouse_pos[1] + game.CAMERA.y

        if self.resizing:
            self.w = game.mouse_pos[0] - self.rel_x
            self.h = game.mouse_pos[1] - self.rel_y

        if self.w < 10:
            self.w = 10
        if self.h < 10:
            self.h = 10

    def selected(self, game):
        if not game.check_mouse(0, buffer=True):
            return

        if game.mouse_pos[0] > self.rel_x and game.mouse_pos[0] < self.rel_x + self.w:
            if game.mouse_pos[1] > self.rel_y and game.mouse_pos[1] < self.rel_y + self.h:
                return True
        return False

    def context_menu(self, game):
        # 3 buttons
        # Move button
        # Resize button
        # Delete

        self.move_button = [(self.rel_x, self.rel_y), 20]
        self.size_button = [(self.rel_x + self.w, self.rel_y + self.h), 20]
        self.delete_button = [(self.rel_x + self.w, self.rel_y), 20]

        if game.check_mouse(0):
            if math.dist(game.mouse_pos, self.move_button[0]) < self.move_button[1]:
                # clicking move button
                self.moving = True
            if math.dist(game.mouse_pos, self.size_button[0]) < self.size_button[1]:
                # clicking size button
                self.resizing = True
        else:
            self.moving = False
            self.resizing = False

        if game.check_mouse(0, buffer=True):
            if math.dist(game.mouse_pos, self.delete_button[0]) < self.delete_button[1]:
                # clicking size button
                self.kill()

    def update_draw(self, game):
        pygame.draw.rect(game.win, self.c, (self.rel_x, self.rel_y, self.w, self.h))

        if self.clicked:
            pygame.draw.circle(game.win, (35, 35, 155), self.move_button[0], self.move_button[1])
            pygame.draw.circle(game.win, (35, 155, 35), self.size_button[0], self.size_button[1])
            pygame.draw.circle(game.win, (155, 35, 35), self.delete_button[0], self.delete_button[1])


class test_element(camera_sprite):
    c = (155, 35, 155)

    def __init__(self, pos, size):
        self.x = pos[0]
        self.y = pos[1]

        self.rel_x = pos[0]
        self.rel_y = pos[1]

        self.w = size[0]
        self.h = size[1]

        self.clicked = False
        self.moving = False
        self.resizing = False


class working_level():
    def save():
        pickle.dump()

    def run():
        pass


def main(game):
    game.CAMERA = camera((0, 0), (game.win_w, game.win_h))
    game.add_sprite(game.CAMERA)

    game.add_sprite(test_element((50, 50), (200, 200)))
    game.add_sprite(test_element((500, 500), (200, 200)))

    game.TOOLBAR = toolbar((1520, 0), (400, 1080), game)
    game.add_sprite(game.TOOLBAR)

    while game.run:
        game.update_keys()
        game.update_draw()
        game.update_scaled()
        game.update_state()

    pygame.quit()


game = game_info(
                name="the mario maker killer",
                win_w=1920,
                win_h=1080,
                user_w=1920,
                user_h=1080,
                bg=(175, 175, 175),
                framecap=60,
                show_framerate=False,
                quit_key=pygame.K_ESCAPE)

main(game)
