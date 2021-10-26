from gameinfo import game_info, pygame, math, random, gameloop
from sprite_class import sprite
import pickle

import elements


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


class func_button(sprite):
    layer = "UI"

    def __init__(self, pos, size, function, args):
        self.x = pos[0]
        self.y = pos[1]

        self.w = size[0]
        self.h = size[1]

        self.FUNC = function
        self.args = args

    def clicked(self, game):
        if not game.check_mouse(0, buffer=True):
            return

        if game.mouse_pos[0] > self.x and game.mouse_pos[0] < self.x + self.w:
            if game.mouse_pos[1] > self.y and game.mouse_pos[1] < self.y + self.h:
                return True
        return False

    def update_move(self, game):
        if self.clicked(game):
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
            spawn_pos = (game.CAMERA.x + 800, game.CAMERA.y + 400)

            new_sprite = elements.test_element(spawn_pos, (100, 100))
            game.add_sprite(new_sprite)
            new_sprite.context_menu(game)
            new_sprite.clicked = True
            game.SELECTION_MANAGER.select_element = new_sprite

        self.TABS = {
            "TERRAIN" : [func_button((self.x + 20, self.y + 120), (self.w - 40, 80), spawn_block, [game])]
        }

        self.current_tab = "TERRAIN"

    def update_move(self, game):
        for button in self.TABS[self.current_tab]:
            button.update_move(game)

    def update_draw(self, game):
        pygame.draw.rect(game.win, self.c, (self.x, self.y, self.w, self.h))
        for button in self.TABS[self.current_tab]:
            button.update_draw(game)


class working_level():
    def save():
        pickle.dump()

    def run():
        pass


def main(game):
    game.CAMERA = camera((0, 0), (game.win_w, game.win_h))
    game.add_sprite(game.CAMERA)

    game.SELECTION_MANAGER = elements.sprite_layer_manager()
    game.add_sprite(game.SELECTION_MANAGER)

    game.add_sprite(elements.test_element((50, 50), (200, 200)))
    game.add_sprite(elements.test_element((500, 500), (200, 200)))

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
                user_w=1280,
                user_h=720,
                bg=(175, 175, 175),
                framecap=60,
                show_framerate=False,
                quit_key=pygame.K_ESCAPE)

main(game)
