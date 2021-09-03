import particles
import random
import draw_utils as drawu


def explosion(game, part, number, pos, **kwargs):

    defaults = {
        "randcol" : False,
        "layer" : "HIGHPARTICLE",
        "randspeed" : False,
        "lifetime" : 30
    }

    non_params = ("randcol", "layer", "randspeed")

    # Particles need <pos, size, speed, angle, colour, lifetime>
    # Provided by this function: angle

    for d in defaults:
        if d not in kwargs:
            kwargs[d] = defaults[d]

    params = {}
    for k in kwargs:
        if k not in non_params:
            params[k] = kwargs[k]

    # yo converT bool to int?????
    expand_speed = int(kwargs['randcol']) + kwargs['speed']
    surf = particles.part_surface(pos, expand_speed, kwargs['lifetime'])
    surf.layer = kwargs['layer']

    params['pos'] = (surf.w/2, surf.h/2)

    for p in range(number):
        params['angle'] = random.randint(0, 360)

        r_speed = kwargs['randspeed']
        if r_speed is not False:
            params['speed'] = random.randint(kwargs['speed'] - r_speed, kwargs['speed'] + r_speed)

        r_col = kwargs['randcol']
        if r_col is not False:
            params['colour'] = drawu.rgb.randomize(kwargs['colour'], r_col*-1, r_col)

        new_part = part(**params)
        surf.add_part(new_part, game)

    game.add_sprite(surf)
