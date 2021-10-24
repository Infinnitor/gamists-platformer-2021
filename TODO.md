# Game todo:

- [ ] Add pause screen

- [ ] Objects that need game in __init__ should get game decorators

- [ ] Experiment with save file
    - [ ] Saving gameinfo object?!?!?!?!?!
    - [ ] Collectibles dictionary

- [x] - Change generation of surfaces for level_elements:
    - [x] - Allow for the use of larger textures
    - [x] - Create more optimised behaviour for generative textures
    - [x] - Make pixels on tv static texture larger

- [x] - Refactor game.purge_sprites
    - [x] - Use list of sprites to exclude instead of include in purge

- [x] - Add funny pogo stick
    - [x] - Add pogo_points

- [x] Refactor text_level

- [x] Clean up player death code

- [x] Camera stuff:
    - [x] - Move camera to its own file
    - [x] - Camera colliders to camera body

- [x] Add LevelTransition:
    - [x] - Room starting position
    - [x] - Multiple entrances and exits?
    - [x] - Make better


# LevelBuild todo:

- [ ] - Create moving blocks
    - Player could ride on them (hard)
    - Maybe enemies???
    - Moving hazard blocks

- [ ] - Level Editor?!?!?!!??!?!
    - [x] - Make draggable blocks
    - [ ] - Everything else

- [x] - New(er) syntax for <level>.txt???
    - OLD: (pos) (size) (type) <some args>
    - NEW: (pos) (size) (type) (type-converted args)

- [x] - Create checkpoint tile
    - Orange 2x2 that turns yellow when you hit it - setting it to your current checkpoint

- [x] - New syntax for <level>.txt
    - OLD: (pos) (size) (colour)
    - NEW: (pos) (size) (type)


# cANCELLED

> Reason: camera colliders discontinued

- Change camera collider generation in LevelBuild:
    - LevelBuild will automatically create camera colliders around the level
    - Camera colliders can overlap level transitions (maybe???)

> Reason: Doesn't really need doing

- Refactor text_player
