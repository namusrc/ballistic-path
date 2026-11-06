# Ballistic Path

**Welcome to Ballistic Path!**

In the game, the player use a gun to destroy the target.
There are multiple types of objects in the field mirrors and boxes are added.
The player freely interact with them: mirrors are used to change the path of the bullet, and the box will occupy the space to stop it.
The player can use 'w', 'a', 's', 'd' to move the movable objects. Moreover, you can press 'r' to rotate the objects. Remember there is only one bullet in the gun. So use the only chance, click 'F' to crush every target!

## Run Instructions
> python main.py



























## Game Purpose
    Shoot the target
## Rules
    1.Only one bullet in the gun
    2.The mirror can reflect the bullet
    3.Shoot the blocks will lose the game
    4.Use w a s d to move the objects
    5.Use r to rotate the gun and mirror
    6.'f' is the bottom of fire
    7.press 'enter' to go to the next level
## Subclasses
    J7
## Container Version
    2026-V3
## Tests and Known Limitations
tests:
    1.The gun can only move in the edge of the terminal
    2.The mirror can rotate and move 
    3.The block can move 
    4.The bullet can move and be reflect by the correct direction
    5.Objects can not move onto other objects or outside the edge
    6.the target can be destoried
    7.the screen can show wether the player is win or lose
limitations:
    1.no sound 
    2.can not restart game after level_4
    3.if the bullet hit the wall, the game do not restart

## Contributions and sources
contribution:
sources:
1    Liang used Gimini 3.1 flash to improve the readability of the bullet reflection logic
2    liang used Gimini 3.1 flash to generate code to show the time the palyer need to finish the game
