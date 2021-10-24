from pygame import transform, draw


# Sprite skeleton class
class sprite():

    def __repr__(self):
        self.highlight = 30
        return f"{self.layer} at position {self.x}, {self.y}"

    def update_move(self, game):
        pass

    def update_draw(self, game):
        pass

    def update_destroy(self, game):
        pass

    def update_highlight(self, game):
        if self.highlight > 0:
            self.draw_highlight(game)
            self.highlight -= 1

    def draw_highlight(self, game):
        try:
            highlight_r = self.r
        except AttributeError:
            highlight_r = 10

        draw.circle(game.win, (35, 155, 35), (self.x, self.y), highlight_r)

    def add_default_attr(self, game):
        try:
            self.layer
        except AttributeError:
            print(f'No layer for {self}')
            raise AttributeError

        try:
            self.persistent
        except AttributeError:
            self.persistent = False

        self.destroy = False
        self.destroying = False
        self.highlight = 0

        # self.add_class_attr(game)

    def add_class_attr(self, game):
        pass

    def kill(self):
        self.destroy = True

    def onscreen(self, game):
        try:
            r = self.r
        except AttributeError:
            r = 0

        if self.x < 0 - r or self.x > game.win_w + r:
            return False
        if self.y < 0 - r or self.y > game.win_h + r:
            return False

        return True

    def center_pos(self, image, pos=None):

        if pos is None:
            pos = (self.x, self.y)

        x = pos[0] - (image.get_width() // 2)
        y = pos[1] - (image.get_height() // 2)

        return x, y

    def blit_center(self, surface, image, dest=None):
        if dest is None:
            dest = (self.x, self.y)

        b_x = dest[0] - image.get_width()//2
        b_y = dest[1] - image.get_height()//2

        surface.blit(image, (b_x, b_y))

    def blit_rotate(self, surface, image, angle):
        img = transform.rotate(image, angle)

        b_x = self.x - img.get_width()//2
        b_y = self.y - img.get_height()//2

        surface.blit(img, (b_x, b_y))
