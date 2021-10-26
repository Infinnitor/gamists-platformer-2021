from pygame import draw
from sprite_class import sprite
import math


class sprite_layer_manager(sprite):
    layer = "MANAGER"

    def __init__(self):
        self.select_element = None

    def update_move(self, game):
        if game.check_mouse(0):
            context_btn_clicked = False

            if self.select_element is not None:
                for b in self.select_element.context_buttons:
                    if b.get_select(game):
                        context_btn_clicked = True
                        break

            if not context_btn_clicked and game.check_mouse(0, buffer=True):
                for s in game.sprites["TERRAIN"]:
                    if s.mouse_hover(game):
                        self.select_element = s
                        return

                self.select_element = None


class camera_sprite(sprite):

    layer = "TERRAIN"

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

        self.context_buttons = []

    class context_btn():
        def __init__(b, radius, type):
            b.r = radius
            b.type = type

            if b.type == "MOVE":
                b.c = (35, 35, 155)
            elif b.type == "SIZE":
                b.c = (35, 155, 35)
            else:
                b.c = (155, 35, 35)

            b.clicked = False

        def get_select(b, game):
            if math.dist((b.x, b.y), game.mouse_pos) < b.r:
                b.clicked = True
                return True

            b.clicked = False
            return False

        def update_move(b, parent):
            if b.type == "MOVE":
                b.x = parent.rel_x
                b.y = parent.rel_y

            elif b.type == "SIZE":
                b.x = parent.rel_x + parent.w
                b.y = parent.rel_y + parent.h

            else:
                b.x = parent.rel_x + parent.w
                b.y = parent.rel_y

        def update_draw(b, game):
            draw.circle(game.win, b.c, (b.x, b.y), b.r)

    def update_move(self, game):
        self.rel_x, self.rel_y = game.CAMERA.get_rel(self)

        # Condition
        self.clicked = (game.SELECTION_MANAGER.select_element is self)

        if self.clicked:
            self.context_menu(game)

        else:
            self.moving = False
            self.resizing = False
            self.context_buttons = []

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

    def mouse_hover(self, game):
        if game.mouse_pos[0] > self.rel_x and game.mouse_pos[0] < self.rel_x + self.w:
            if game.mouse_pos[1] > self.rel_y and game.mouse_pos[1] < self.rel_y + self.h:
                return True
        return False

    def context_menu(self, game):
        # 3 buttons
        # Move button
        # Resize button
        # Delete

        if not self.context_buttons:
            self.context_buttons = [self.context_btn(20, "MOVE"), self.context_btn(20, "SIZE"), self.context_btn(20, "DEL")]

        for b in self.context_buttons:
            b.update_move(self)

        if game.check_mouse(0):
            for b in self.context_buttons:
                if b.clicked:
                    if b.type == "MOVE":
                        self.moving = True
                    elif b.type == "SIZE":
                        self.resizing = True
                    break

        else:
            self.moving = False
            self.resizing = False

        if game.check_mouse(0, buffer=True):
            if self.context_buttons[-1].clicked:
                self.kill()

    def update_draw(self, game):
        draw.rect(game.win, self.c, (self.rel_x, self.rel_y, self.w, self.h))

        if self.clicked:
            for b in self.context_buttons:
                b.update_draw(game)


class test_element(camera_sprite):
    c = (155, 35, 155)

    # hehe there is nothing here

    # we will make this a proper child class when we do the fukn level elements and shit
