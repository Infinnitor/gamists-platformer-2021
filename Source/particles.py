import math
import copy

from pygame import draw, Surface
from sprite_class import sprite
from colour_manager import colours


class particle(sprite):
    layer = "HIGHPARTICLE"

    def __init__(self, pos, size, speed, angle, colour, lifetime):
        self.x = pos[0]
        self.y = pos[1]
        self.size = size

        self.speed = speed
        self.angle_calc(angle)

        self.c = colour

        self.life_calc(lifetime)

    def angle_calc(self, angle):
        self.a = angle
        self.xmove = math.cos(self.a) * self.speed
        self.ymove = math.sin(self.a) * self.speed

    def life_calc(self, lifetime):
        self.lifetime = lifetime
        self.life = 0
        self.lifeloss = self.size / self.lifetime

    def update_move(self, game):
        self.x += self.xmove
        self.y += self.ymove

        self.size -= self.lifeloss

        self.life += 1
        if self.life > self.lifetime:
            self.destroy = True


class circle(particle):
    # Use an alt surface to make it easier to draw the particles with camera stuff
    def update_draw(self, surface):
        draw.circle(surface, self.c, (self.x, self.y), self.size)


class square(particle):
    def update_draw(self, surface):
        draw.circle(surface, self.c, (self.x + self.size//2, self.y + self.size//2, self.size, self.size))


class diamond(particle):
    def update_draw(self, surface):

        s = self.size//2
        shape = (
            (self.x + s, self.y),
            (self.x + self.side, self.y + s),
            (self.x + s, self.y + self.side),
            (self.x, self.y + s)
        )

        draw.polygon(surface, self.c, shape)


class part_surface(sprite):
    layer = "HIGHPARTICLE"

    def __init__(self, pos, speed, lifetime):
        self.x = pos[0]
        self.y = pos[1]

        side = speed * lifetime * 2
        self.w = side
        self.h = side

        self.surface = Surface((self.w, self.h))
        self.surface.set_colorkey(colours.colourkey)

        self.particles = []

    def add_part(self, part, game):
        part.add_default_attr(game)
        self.particles.append(part)

    def update_draw(self, game):
        self.surface.fill(colours.colourkey)

        valid_particles = []
        for p in self.particles:
            p.update_move(game)
            p.update_draw(self.surface)
            if not p.destroy:
                valid_particles.append(p)

        self.particles = valid_particles
        if not self.particles:
            self.kill()
            return

        rel_x = self.x - game.camera_obj.x
        rel_y = self.y - game.camera_obj.y

        game.win.blit(self.surface, (rel_x - self.w/2, rel_y-self.h/2))


class temp():
    def __init__(self, particle):
        self.template = particle

    def copy(self):
        return copy.copy(self.template)

    def modify(self, pos=None, size=None, speed=None, angle=None, colour=None, lifetime=None):
        c = self.copy()

        if pos is not None:
            c.x = pos[0]
            c.y = pos[1]

        if size is not None:
            c.size = size
        if speed is not None:
            c.speed = speed
        if angle is not None:
            c.angle_calc(angle)
        if colour is not None:
            c.c = colour
        if lifetime is not None:
            c.life_calc(lifetime)

        return temp(c)

    def get(self, pos, size=None, speed=None, angle=None, colour=None, lifetime=None):
        mod = self.modify(pos, size, speed, angle, colour, lifetime)

        return mod.copy()


class particle_templates_manager():

    def __init__(self):
        self.circle = temp(circle(pos=(0, 0), size=10, speed=1, angle=0, lifetime=30, colour=(0, 255, 0)))
        self.square = temp(circle(pos=(0, 0), size=10, speed=1, angle=0, lifetime=30, colour=(0, 255, 0)))
        self.diamond = temp(circle(pos=(0, 0), size=10, speed=1, angle=0, lifetime=30, colour=(0, 255, 0)))


TEMPLATES = particle_templates_manager()
