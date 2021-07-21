import math
import random


def circle_collide(p, q, add=[], attr=True):

    if attr:
        p = (p.x, p.y, p.r)
        q = (q.x, q.y, q.r)

    if math.dist((p[0], p[1]), (q[0], q[1])) < p[2] + q[2] + sum(add):
        return True
    return False


def rect_collision(rect1, rect2):

    if rect1.x + rect1.w > rect2.x and rect1.x < rect2.x + rect2.w:
        if rect1.y + rect1.h > rect2.y and rect1.y < rect2.y + rect2.h:
            return True

    return False


def midpoint(p, q, attr=True, rounding=False):
    if attr:
        ret = [(p.x + q.x) / 2, (p.y + q.y) / 2]
    else:
        ret = [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2]

    if rounding:
        ret = [round(r) for r in ret]
    return ret


# class shape():
#     def center_square(pos, side):
#         s = side/2
#         return (pos[0] - s, pos[1] - s, pos[0] + s, pos[1] + s)
#
#     def center_triangle(pos, d):
#         return (pos[0], )


class offset():
    def update_pos(self, pos=(0, 0)):
        if self.parent is not None:
            pos = (self.parent.x, self.parent.y)

        self.x = pos[0] + self.offset_x
        self.y = pos[1] + self.offset_y

    def get_pos(self, pos=(0, 0)):
        self.update_pos(pos)

        return [self.x, self.y]


class offset_point(offset):
    def __init__(self, parent, offset):

        self.parent = parent

        self.offset_x = offset[0]
        self.offset_y = offset[1]

        self.update_pos()


class offset_circle(offset):
    def __init__(self, parent, offset, radius):

        self.parent = parent

        self.offset_x = offset[0]
        self.offset_y = offset[1]

        self.update_pos()
        self.r = radius


class sine_bob():
    def __init__(self, wavelength, period):
        self.w = wavelength
        self.p = period

        self.x = 0
        self.y_mod = 0

    def update_pos(self):
        self.x += 0.01
        self.y_mod = self.w * math.sin(self.x * self.p)

    def get_pos(self, update=True):
        if update:
            self.update_pos()
            return self.y_mod
        else:
            return 0


class polygon():
    def caesarian(points, shift=0):

        shifted_p = [i for i in points]

        if shift == 0:
            shift = random.randint(1, len(points) - 1)

        for s in range(shift):
            shifted_p.insert(0, shifted_p.pop(-1))

        return shifted_p

    def anchor(points, anchor):
        return [(x - anchor[0], y - anchor[1]) for x, y in points]

    def adjust(polygon, x=0, y=0):
        new_polygon = []
        for point in polygon:
            new_polygon.append((point[0] + x, point[1] + y))

        return new_polygon

    def rotate(points, anchor, rotation):
        rotated_p = []
        r_mod = math.radians(rotation)

        for x, y in points:
            adj = x - anchor[0]
            opp = y - anchor[1]

            hyp = math.sqrt(adj**2 + opp**2)

            a = math.atan2(opp, adj)
            a += r_mod

            rotated_p.append([math.cos(a) * hyp, math.sin(a) * hyp])

        return rotated_p


class morph():

    def __len__(self):
        return len(self.shapes)

    def log_shapes(self, shapes, shift=False):
        self.shapes = list(shapes)
        assert sum([len(s) for s in self.shapes]) == max([len(s) for s in self.shapes]) * len(self.shapes), "All shapes must have an equal amount of points"

        if shift is not False:
            for s in range(len(self.shapes)):
                if s % 2 == 0:
                    self.shapes[s] = polygon.caesarian(self.shapes[s], shift)

        self.polygon = self.shapes[0]

        self.step = 1
        self.iter = 0

        self.morphing = False
        self.target = 0

        self.init_morph(0, frames=1)

    def add(self, new_shape):
        assert len(new_shape) == max([len(s) for s in self.shapes]), "Number of points on added shape must be equal to that of existing shapes"
        self.shapes.append(new_shape)

    def init_morph(self, target, frames):
        if self.shapes[target] == self.polygon or target == self.target:
            return

        self.morph1 = self.polygon
        self.morph2 = self.shapes[target]

        self.morphing = True
        self.target = target

        self.iter = 0
        self.step = 100 / frames

        self.init_morph_calc()

    def init_morph_calc(self):

        self.sorted_points_mv = []
        for a, b in zip(self.morph1, self.morph2):
            x_d = b[0] - a[0]
            y_d = b[1] - a[1]

            self.sorted_points_mv.append([x_d, y_d])

    def morph(self):
        morph_polygon = []
        for c, d in zip(self.morph1, self.sorted_points_mv):
            mv_x = c[0] + (d[0] * (self.iter / 100))
            mv_y = c[1] + (d[1] * (self.iter / 100))
            morph_polygon.append([mv_x, mv_y])

        self.polygon = morph_polygon


class morphpolygon(morph):

    def __init__(self, *shapes, shift=False):
        self.log_shapes(shapes, shift)

    def get(self):
        if self.iter < 100:
            self.iter += self.step
        else:
            self.iter = 100
            self.morphing = False

        if self.morphing is True:
            self.morph()

        return self.polygon


class offset_morphpolygon(offset, morph):
    def __init__(self, *shapes, offset, parent=None, shift=False):

        self.offset_x = offset[0]
        self.offset_y = offset[1]

        self.parent = parent

        self.log_shapes(shapes, shift)

    def get(self, pos=(0, 0)):
        if self.iter < 100:
            self.iter += self.step
        else:
            self.iter = 100
            self.morphing = False

        self.update_pos(pos)

        if self.morphing is True:
            self.morph()

        ret_polygon = []
        for x, y in self.polygon:
            ret_polygon.append([x + self.x, y + self.y])

        return ret_polygon
