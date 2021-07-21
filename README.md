# gamists-platformer-2021
the mario killer

# About config.txt:

ALL THESE VALUES SHOULD BE POSITIVE

- horizontal acceleration: The force that pushes the player left or right (added to their X speed every frame LEFT or RIGHT are pressed). default : 1
- gravity: The force that is pushing down on the player (added to their Y speed every frame). default : 0.5
- vertical speed cap: the players Y speed can not go past this number. default : 11
- horizontal speed cap: the players X speed can not go past this number. default : 7
- jump strength: the vertical momentum that is added to the Y speed every frame the jump key is held within the min/max window. default : 15
- held jump min: the amount of frames where pressing JUMP doesn't add any additional jump strength to the vertical momentum. default : 5
- held jump max: the amount of frames where you can no longer add additional jump strength to the vertical momentum. default : 10

> if the held jump min is 5, you have 5 frames to press space and let go to have the smallest jump possible

- start x: the X location on the screen (in pixels) where the player starts. default : 500
- start y: the Y location on the screen (in pixels) where the player starts. default : 500
- player width: the width of the player (px). default : 50
- player height: the height of the player (px). default : 50
