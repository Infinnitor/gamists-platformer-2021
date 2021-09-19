# Game todo:

- [ ] - Change generation of surfaces for level_elements:
    - [x] - Allow for the use of larger textures
    - [x] - Create more optimised behaviour for generative textures
    - [ ] - Make pixels on tv static texture larger

- [ ] Add pause screen

- [ ] Add funny pogo stick

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
