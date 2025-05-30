# Color Echo Maze Game

A maze exploration game where you use color pulses to reveal hidden elements in the environment.

## Game Overview

In Color Echo Maze, you navigate through a maze using sound and color pulses to reveal different elements:
- **Red Pulses (R key)**: Reveal traps that will end your game if stepped on
- **Green Pulses (G key)**: Reveal safe paths to help guide your way
- **Blue Pulses (B key)**: Reveal portals that allow you to complete the level

## Controls

- **Arrow Keys**: Move your character (yellow circle)
- **R Key**: Emit a red pulse
- **G Key**: Emit a green pulse
- **B Key**: Emit a blue pulse
- **F11 Key**: Toggle fullscreen mode
- **ESC Key**: Quit the game
- **SPACE Key**: Restart level (when game over) or proceed to next level (when level complete)

## Game Elements

- **Yellow Circle**: Your character
- **White Blocks**: Regular walls
- **Red Blocks**: Traps (game over if stepped on)
- **Green Blocks**: Safe paths
- **Blue Blocks**: Portals (level exit)
- **Light Gray Blocks**: Reflective walls
- **Dark Gray Blocks**: Absorbing walls
- **Purple Blocks**: Moving walls

## Sound Effects

The game includes sound effects for:
- Player movement
- Red, green, and blue pulse emissions
- Game over (when hitting a trap)
- Level completion

## Fullscreen Mode

The game launches in fullscreen mode by default. You can toggle between fullscreen and windowed mode by pressing F11.

## Requirements

- Python 3.x
- Pygame library

## Sound Files

You need to place the following sound files in the same directory as the game:
- `move.wav`: Player movement sound
- `red_pulse.wav`: Red echo sound
- `green_pulse.wav`: Green echo sound
- `blue_pulse.wav`: Blue echo sound
- `game_over.wav`: Game over sound
- `level_complete.wav`: Level complete sound

## How to Run

```
python color_echo_maze.py
```

## Game Mechanics

- Each pulse type consumes energy that regenerates over time
- The maze gets larger and more complex as you progress through levels
- Different wall types interact with pulses differently
- Moving walls change position periodically
- The camera follows the player smoothly as they move through the maze
