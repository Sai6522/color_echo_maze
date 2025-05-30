# Color Echo Maze

A pulse-based maze exploration game where you navigate through a procedurally generated maze using color-coded pulses to reveal hidden elements.

![Color Echo Maze](https://github.com/yourusername/color-echo-maze/raw/main/screenshots/gameplay.png)

## Game Description

In Color Echo Maze, you navigate through a mysterious maze where most of the environment is hidden from view. You must use special color pulses to reveal different elements of the maze:

- **Red Pulses**: Reveal dangerous traps that must be avoided
- **Green Pulses**: Reveal safe paths to guide your journey
- **Blue Pulses**: Reveal portals that allow you to advance to the next level

The game features automatic pulses every 4 seconds, but you can also manually trigger pulses if you have enough energy. Navigate carefully, avoid traps, and find the portal before time runs out!

## Features

- Procedurally generated mazes that increase in size and complexity with each level
- Dynamic visibility system based on color-coded pulses
- Energy management system for pulse emissions
- Multiple wall types including reflective, absorbing, and moving walls
- Time-based challenges with increasing difficulty
- Smooth camera movement that follows the player
- Fullscreen support with resolution-independent UI
- Sound effects for movement, pulses, and game events

## Controls

- **Arrow Keys**: Move the player character
- **R**: Emit a red pulse (reveals traps)
- **G**: Emit a green pulse (reveals safe paths)
- **B**: Emit a blue pulse (reveals portals)
- **F11**: Toggle fullscreen mode
- **ESC**: Quit the game
- **SPACE**: Restart level (when game over) or proceed to next level (when level complete)

## Game Elements

- **Yellow Circle**: Player character
- **Red Squares**: Traps (game over if touched)
- **Green Squares**: Safe paths
- **Blue Squares**: Portal to next level
- **White Squares**: Regular walls
- **Light Gray Squares**: Reflective walls
- **Dark Gray Squares**: Absorbing walls
- **Purple Squares**: Moving walls

## Requirements

- Python 3.6+
- Pygame library

## Installation

1. Clone this repository:
```
git clone https://github.com/Sai6522/color_echo_maze.git
cd color_echo_maze
```

2. Install the required dependencies:
```
pip install pygame
```

3. Run the game:
```
python main.py
```

## Game Structure

- `main.py`: Main game file containing all game logic
- `sounds/`: Directory containing sound effects
  - `move.wav`: Player movement sound
  - `red_pulse.wav`: Red pulse emission sound
  - `green_pulse.wav`: Green pulse emission sound
  - `blue_pulse.wav`: Blue pulse emission sound
  - `game_over.wav`: Game over sound
  - `level_complete.wav`: Level completion sound

## Game Mechanics

### Maze Generation
Each maze is procedurally generated with increasing complexity as you progress through levels. The algorithm ensures there's always a valid path from the starting position to the portal.

### Pulse System
Pulses expand outward from the player, revealing different elements of the maze based on their color. Energy for pulses regenerates over time.

### Moving Walls
In higher levels, some walls move around the maze, adding an extra challenge to navigation.

### Time Limit
Each level has a time limit that increases with level progression. You must find the portal before time runs out.

## Tips for Players

- Pay attention to the energy bars and use manual pulses strategically
- Remember the locations of traps and safe paths as they're revealed
- Plan your route to the portal carefully
- In higher levels, be cautious of moving walls that can block your path
- The time limit increases with each level, but so does the maze size

## Try It Online

You can play Color Echo Maze online on Replit: [Color Echo Maze on Replit](https://replit.com/@VENKATA-SAI-PR4/colorechomaze)

## Future Enhancements

- Additional pulse types with unique effects
- Power-ups and collectibles
- Multiple game modes
- High score system
- Custom maze editor

## Credits

- Game design and programming: Venkata Sai Prasad Pulaparthi
- Sound effects: [Source of sound effects from Mixkit]
- Font: Arial

---

Made with ❤️ and Amazon Q CLI
