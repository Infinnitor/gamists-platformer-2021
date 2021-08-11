# Game todo:

- [ ] - Change generation of surfaces for level_elements:
    - [ ] - Allow for the use of larger textures
    - [ ] - Create more optimised behaviour for generative textures
    - [ ] - Make pixels on tv static texture larger

- [x] Refactor text_level

- [ ] Refactor text_player

- [x] Clean up player death code

- [x] Camera stuff:
    - [x] - Move camera to its own file
    - [x] - Camera colliders to camera body

- [x] Add LevelTransition:
    - [x] - Room starting position
    - [x] - Multiple entrances and exits?
    - [ ] - Make better


# LevelBuild todo:

- [ ] - Change camera collider generation in LevelBuild:
    - [ ] - LevelBuild will automatically create camera colliders around the level
    - [ ] - Camera colliders can overlap level transitions (maybe???)

- [x] - Create checkpoint tile
    - Orange 2x2 that turns yellow when you hit it - setting it to your current checkpoint

- [x] - New syntax for level.txt
    - OLD: (pos) (size) (colour)
    - NEW: (pos) (size) (type)
