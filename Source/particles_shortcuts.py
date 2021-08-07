import particles
import random
import draw_utils as drawu


def explosion(number, pos, speed, colour, game, lifetime=30, randcol=False, layer="HIGHPARTICLE"):
    surf = particles.part_surface(pos, speed, lifetime)
    surf.layer = layer

    center = (surf.w/2, surf.h/2)

    for p in range(number):

        angle = random.randint(0, 360)

        final_colour = colour
        if randcol is True:
            final_colour = drawu.rgb.randomize(colour)

        new_part = particles.TEMPLATES.circle.get(pos=center, size=15, speed=speed, angle=angle, lifetime=lifetime, colour=final_colour)
        surf.add_part(new_part)

    game.add_sprite(surf)
