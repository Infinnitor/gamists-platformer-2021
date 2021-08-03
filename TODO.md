# Game todo:

- [ ] - Change generation of surfaces for level_elements:
    - [ ] - Allow for the use of larger textures
    - [ ] - Create more optimised behaviour for generative textures
    - [ ] - Make pixels on tv static texture larger

- [ ] - Change some names:
     - [ ] - Camera colliders to camera body

- [ ] Refactor text_level

- [ ] Refactor text_player


- [x] Add LevelTransition:
    - [x] - Room starting position
    - [x] - Multiple entrances and exits?


# LevelBuild todo:

- [x] - Create checkpoint tile
    - Orange 2x2 that turns yellow when you hit it - setting it to your current checkpoint

- [x] - New syntax for level.txt
    - OLD: (pos) (size) (colour)
    - NEW: (pos) (size) (type)

    - [ ] - Change camera collider generation in LevelBuild:
        - [ ] - LevelBuild will automatically create camera colliders around the level
        - [ ] - Camera colliders can overlap level transitions (maybe???)
