import particles
import random
import draw_utils as drawu


def explosion(number, pos, part, randcol=False, layer="HIGHPARTICLE", game=None):
    assert game is not None, f"You forgor to pass in game"

    surf = particles.part_surface(pos, part.template.speed, part.template.lifetime)
    surf.layer = layer

    center = (surf.w/2, surf.h/2)

    for p in range(number):

        angle = random.randint(0, 360)

        final_colour = part.template.c
        if randcol is True:
            final_colour = drawu.rgb.randomize(final_colour)

        new_part = part.get(pos=center, angle=angle, colour=final_colour)
        surf.add_part(new_part)

    game.add_sprite(surf)
