# Ballistic Path

**Welcome to Ballistic Path!**

This is a Python puzzle game that turns a midnight vault heist into a test of aim and ingenuity. Guided by King, you’re sent into the vault with a simple warning: every run gets one shot, and every lock must be broken. The repository contains the game and its levels, where mirrors, boxes, and carefully placed targets make each challenge a new part of the adventure.

## Run Instructions
> python main.py

## Game Purpose

Plan your escape-worthy shots: move and rotate objects, angle mirrors to redirect the bullet, and clear each target without wasting your single chance or hitting a block. As you progress through the levels, King’s messages keep the pressure on. There’s money to be made, but time is running out. Can you outsmart the vault’s obstacles and make every shot count?

## Rules
1. You have only one bullet for each attempt, so plan your shot carefully.
2. Mirrors reflect the bullet and can help guide it toward targets.
3. Hitting a sturdy block means losing the attempt.
4. Use W, A, S, D to move movable objects.
5. Press R to rotate the gun or mirrors.
6. Press F to fire.
7. Destroy all targets to clear the level.
8. Press Enter to continue to the next level.

## Subclasses
    J07: Yasasvi Bandi, Jiacheng Liang, Xinhao Chen, Chanyeong Park
## Container Version
    2026-V3
## Tests and Known Limitations
### Tests
One-off engine checks were run with Python 3.14.10; all 15 assertions passed. They verified that:
- Levels 0–6 and their objects load successfully.
- Movable objects can move into empty cells, while occupied cells block movement.
- The gun rotates and remains on the grid perimeter.
- A shot can reflect from a mirror and destroy a target.
- Hitting a sturdy box causes a loss, and reloading a level resets the game state.
- A shot leaving the grid is removed, but does not trigger a loss or restart.

### Known Limitations
- When a bullet leaves the grid, it disappears while the game remains in the running state; the player is not prompted to retry.
- There is no music or dedicated sound effects; the loss notification relies on the terminal bell.
- The game lacks visual hint that the gun can only be moved in the outer ring, due to limited number of supported colors in terminals. Decided not to use [true color](https://docs.python.org/3/library/curses.html) for the sake of cross-platform compatibility.

## Contributions and Sources
### 1. Game Design & Assets

- Game Concept & Core Mechanics Design - Chanyeong Park, Jiacheng Liang, Yasasvi Bandi
- Game Balance & Difficulty Tuning - Yasasvi Bandi
- Level Design Management - Yasasvi Bandi
- Level 1 Design & Implementation - Yasasvi Bandi
- Level 2 Design & Implementation - Yasasvi Bandi
- Level 3 Design & Implementation - Yasasvi Bandi
- Level 4 Design & Implementation - Yasasvi Bandi
- Level 5 Design & Implementation - Yasasvi Bandi
- Level 6 Design & Implementation - Yasasvi Bandi
- Debug / Test Level Design - Chanyeong Park
- Visual Assets & Animations - Jiacheng Liang, Chanyeong Park
- UI / Menu Design (Start, Pause, Game Over) - Jiacheng Liang, Chanyeong Park
- Story - Yasasvi Bandi, Chanyeong Park

### 2. Core Programming & Systems

- Grid & Map Architecture - Chanyeong Park
- Level Loading & Parsing - Jiacheng Liang, Chanyeong Park
- Object & Entity Class Design - Jiacheng Liang, Chanyeong Park
- Rendering & Graphics Pipeline - Jiacheng Liang, Chanyeong Park
- Input Handling & Controls - Chanyeong Park
- Game State Management (Menu, Play, Win/Lose) - Yasasvi Bandi, Chanyeong Park
- Object Movement & Pathing - Jiacheng Liang, Chanyeong Park
- Object Rotation - Jiacheng Liang, Chanyeong Park, Xinhao Chen
- Shooting Mechanism - Jiacheng Liang, Chanyeong Park
- Collision Detection & Damage Logic - Jiacheng Liang, Chanyeong Park
- Scoring & Progression System - Yasasvi Bandi, Chanyeong Park

### 3. Debugging, Testing & Polish

- Debug Mode Implementation - Chanyeong Park
- Debug Message & Logging System - Jiacheng Liang, Chanyeong Park
- Bug Fixing & Edge Case Handling - Chanyeong Park
- Playtesting & Quality Assurance (QA) - Jiacheng Liang, Chanyeong Park, Yasasvi Bandi, Xinhao Chen
- Code Refactoring & Cleaning - Jiacheng Liang, Chanyeong Park

### 4. DevOps & Project Management

- Git / Branch & Pull Request Management - Yasasvi Bandi, Chanyeong Park
- Docker & Container Management - Jiacheng Liang
- Dependency & Build Configuration - Jiacheng Liang, Chanyeong Park
- Meeting Organization & Scheduling - Chanyeong Park
- Task Tracking & Timeline Management - Yasasvi Bandi, Chanyeong Park

### 5. Documentation & Media Delivery

- README Documentation - Xinhao Chen, Chanyeong Park
- Code Comments & Technical Documentation - Jiacheng Liang, Chanyeong Park
- Project Report / Presentation Slides - Chanyeong Park
- Gameplay Recording / Demo Video - Chanyeong Park, Jiacheng Liang, Xinhao Chen
- Video Trailer Production - Xinhao Chen
- Video Editing & Post-Production - Xinhao Chen, Chanyeong Park
- Final Submission Packaging - Jiacheng Liang
