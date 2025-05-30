import pygame
import sys
import time
import os
import random
from enum import Enum
from collections import deque  # Add deque for BFS pathfinding

# Initialize pygame
pygame.init()
pygame.font.init()
pygame.mixer.init()  # Initialize the sound mixer

# Game constants
SCREEN_WIDTH = 800  # Default width, will be overridden in fullscreen
SCREEN_HEIGHT = 600  # Default height, will be overridden in fullscreen
GRID_SIZE = 40
FPS = 60
FULLSCREEN = True  # Set to True to run in fullscreen mode
AUTO_PULSE_INTERVAL = 4.0  # Time between automatic pulses in seconds
BASE_TIME_LIMIT = 200  # Base time limit in seconds for level 1

# Get the current directory of the script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUNDS_DIR = os.path.join(BASE_DIR, 'sounds')

SOUND_MOVE = os.path.join(SOUNDS_DIR, 'move.wav')
SOUND_RED_PULSE = os.path.join(SOUNDS_DIR, 'red_pulse.wav')
SOUND_GREEN_PULSE = os.path.join(SOUNDS_DIR, 'green_pulse.wav')
SOUND_BLUE_PULSE = os.path.join(SOUNDS_DIR, 'blue_pulse.wav')
SOUND_GAME_OVER = os.path.join(SOUNDS_DIR, 'game_over.wav')
SOUND_LEVEL_COMPLETE = os.path.join(SOUNDS_DIR, 'level_complete.wav')

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)

# Pulse duration in seconds
PULSE_DURATION = 3.0

class CellType(Enum):
    EMPTY = 0
    WALL = 1
    TRAP = 2
    SAFE_PATH = 3
    PORTAL = 4
    REFLECTIVE_WALL = 5
    ABSORBING_WALL = 6
    MOVING_WALL = 7

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class PulseType(Enum):
    RED = 0
    GREEN = 1
    BLUE = 2

class Pulse:
    def __init__(self, x, y, pulse_type, maze):
        self.x = x
        self.y = y
        self.type = pulse_type
        self.start_time = time.time()
        self.radius = 0
        self.max_radius = 400
        self.speed = 200  # pixels per second
        self.active = True
        self.maze = maze
        
        # Set color based on pulse type
        if self.type == PulseType.RED:
            self.color = RED
        elif self.type == PulseType.GREEN:
            self.color = GREEN
        else:  # BLUE
            self.color = BLUE
    
    def update(self, dt):
        # Expand the pulse
        self.radius += self.speed * dt
        
        # Check if pulse duration has expired
        if time.time() - self.start_time > PULSE_DURATION or self.radius > self.max_radius:
            self.active = False
    
    def draw(self, screen, camera_offset_x, camera_offset_y):
        if not self.active:
            return
            
        # Calculate transparency based on time left
        time_left = PULSE_DURATION - (time.time() - self.start_time)
        alpha = max(0, min(255, int(255 * (time_left / PULSE_DURATION))))
        
        # Create a surface for the pulse
        pulse_surface = pygame.Surface((SCREEN_WIDTH * 2, SCREEN_HEIGHT * 2), pygame.SRCALPHA)
        
        # Draw the pulse circle with transparency
        try:
            pygame.draw.circle(
                pulse_surface, 
                (*self.color, alpha), 
                (SCREEN_WIDTH, SCREEN_HEIGHT), 
                self.radius, 
                5
            )
        except ValueError:
            # Fallback if there's still an issue with the color
            pygame.draw.circle(
                pulse_surface, 
                (*self.color, 128), 
                (SCREEN_WIDTH, SCREEN_HEIGHT), 
                self.radius, 
                5
            )
        
        # Draw the pulse on the screen
        screen.blit(
            pulse_surface, 
            (-SCREEN_WIDTH + self.x * GRID_SIZE - camera_offset_x, 
             -SCREEN_HEIGHT + self.y * GRID_SIZE - camera_offset_y)
        )

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.pulse_energy = {
            PulseType.RED: 100,
            PulseType.GREEN: 100,
            PulseType.BLUE: 100
        }
        self.energy_regen_rate = 5  # Energy points per second
        self.pulse_cost = 20  # Energy cost per pulse
        self.last_auto_pulse_time = time.time()  # Track time of last auto pulse
    
    def move(self, direction, maze):
        new_x = self.x + direction.value[0]
        new_y = self.y + direction.value[1]
        
        # Check if the new position is valid
        if 0 <= new_x < maze.width and 0 <= new_y < maze.height:
            cell = maze.get_cell(new_x, new_y)
            
            # Can't move through walls
            if cell == CellType.WALL or cell == CellType.REFLECTIVE_WALL or cell == CellType.ABSORBING_WALL or cell == CellType.MOVING_WALL:
                return False
                
            self.x = new_x
            self.y = new_y
            return True
        return False
    
    def emit_pulse(self, pulse_type, maze):
        # Check if player has enough energy
        if self.pulse_energy[pulse_type] >= self.pulse_cost:
            self.pulse_energy[pulse_type] -= self.pulse_cost
            return Pulse(self.x, self.y, pulse_type, maze)
        return None
    
    def regenerate_energy(self, dt):
        for pulse_type in self.pulse_energy:
            self.pulse_energy[pulse_type] = min(100, self.pulse_energy[pulse_type] + self.energy_regen_rate * dt)
    
    def auto_emit_pulse(self, current_time, maze):
        # Check if it's time for an auto pulse (every AUTO_PULSE_INTERVAL seconds)
        if current_time - self.last_auto_pulse_time >= AUTO_PULSE_INTERVAL:
            # Randomly select a pulse type
            pulse_types = list(PulseType)
            random.shuffle(pulse_types)
            
            # Try each pulse type until one succeeds
            for pulse_type in pulse_types:
                pulse = self.emit_pulse(pulse_type, maze)
                if pulse:
                    self.last_auto_pulse_time = current_time
                    return pulse, pulse_type
                    
        return None, None
    
    def draw(self, screen, camera_offset_x, camera_offset_y):
        # Draw player as a yellow circle
        pygame.draw.circle(
            screen, 
            YELLOW, 
            ((self.x * GRID_SIZE) + GRID_SIZE // 2 - camera_offset_x, 
             (self.y * GRID_SIZE) + GRID_SIZE // 2 - camera_offset_y), 
            GRID_SIZE // 2 - 5
        )

class Maze:
    def __init__(self, width, height, level):
        self.width = width
        self.height = height
        self.level = level
        self.grid = [[CellType.EMPTY for _ in range(height)] for _ in range(width)]
        self.visible_grid = [[False for _ in range(height)] for _ in range(width)]
        self.moving_walls = []
        self.portal_position = None
        self.generate_maze()
    
    def generate_maze(self):
        # This is a simple maze generation for demonstration
        # In a real game, you'd want a more sophisticated algorithm
        
        # Add outer walls
        for x in range(self.width):
            self.grid[x][0] = CellType.WALL
            self.grid[x][self.height - 1] = CellType.WALL
        
        for y in range(self.height):
            self.grid[0][y] = CellType.WALL
            self.grid[self.width - 1][y] = CellType.WALL
        
        # Add some random walls
        wall_count = (self.width * self.height) // 5
        for _ in range(wall_count):
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            
            # Skip if this would block the player completely
            if self.would_block_player(x, y):
                continue
                
            # Add different wall types based on level
            if self.level >= 3 and random.random() < 0.2:
                self.grid[x][y] = CellType.REFLECTIVE_WALL
            elif self.level >= 2 and random.random() < 0.2:
                self.grid[x][y] = CellType.ABSORBING_WALL
            elif self.level >= 4 and random.random() < 0.1:
                self.grid[x][y] = CellType.MOVING_WALL
                self.moving_walls.append((x, y, random.choice(list(Direction))))
            else:
                self.grid[x][y] = CellType.WALL
        
        # Add traps
        trap_count = (self.width * self.height) // 10
        for _ in range(trap_count):
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            if self.grid[x][y] == CellType.EMPTY and not self.would_block_player(x, y):
                self.grid[x][y] = CellType.TRAP
        
        # Add safe paths
        safe_path_count = (self.width * self.height) // 8
        for _ in range(safe_path_count):
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            if self.grid[x][y] == CellType.EMPTY:
                self.grid[x][y] = CellType.SAFE_PATH
        
        # Add portal
        while True:
            x = random.randint(self.width // 2, self.width - 2)
            y = random.randint(1, self.height - 2)
            if self.grid[x][y] == CellType.EMPTY:
                self.grid[x][y] = CellType.PORTAL
                self.portal_position = (x, y)
                break
        
        # Make sure the starting area is clear
        for x in range(1, 3):
            for y in range(1, 3):
                self.grid[x][y] = CellType.EMPTY
        
        # Ensure there's a valid path to the portal
        if not self.has_path_to_portal():
            # If no path exists, regenerate the maze
            self.grid = [[CellType.EMPTY for _ in range(self.height)] for _ in range(self.width)]
            self.moving_walls = []
            self.generate_maze()
    
    def would_block_player(self, x, y):
        """Check if placing a wall at (x,y) would block the player completely"""
        # Don't block the starting position
        if x < 3 and y < 3:
            return True
            
        # Don't create 2x2 or larger solid blocks that could trap the player
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                    
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    # Check if this would create a closed area
                    if self.would_create_enclosed_area(x, y):
                        return True
        
        return False
    
    def would_create_enclosed_area(self, wall_x, wall_y):
        """Check if adding a wall at (wall_x, wall_y) would create an enclosed area"""
        # Temporarily place the wall
        original_cell = self.grid[wall_x][wall_y]
        self.grid[wall_x][wall_y] = CellType.WALL
        
        # Check if any empty cells would become enclosed
        for x in range(1, self.width - 1):
            for y in range(1, self.height - 1):
                if self.grid[x][y] == CellType.EMPTY:
                    # Check if this cell has no escape route
                    if self.is_enclosed(x, y):
                        # Restore the original cell and return True (would create enclosed area)
                        self.grid[wall_x][wall_y] = original_cell
                        return True
        
        # Restore the original cell and return False (would not create enclosed area)
        self.grid[wall_x][wall_y] = original_cell
        return False
    
    def is_enclosed(self, x, y):
        """Check if a cell is enclosed by walls with no way out"""
        # Check all four directions
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                cell = self.grid[nx][ny]
                if cell != CellType.WALL and cell != CellType.REFLECTIVE_WALL and cell != CellType.ABSORBING_WALL and cell != CellType.MOVING_WALL:
                    # There's at least one way out
                    return False
        # All directions are blocked
        return True
    
    def has_path_to_portal(self):
        """Check if there's a valid path from the start to the portal using BFS"""
        if not self.portal_position:
            return False
            
        # Starting position
        start = (1, 1)
        goal = self.portal_position
        
        # BFS
        queue = deque([start])
        visited = set([start])
        
        while queue:
            x, y = queue.popleft()
            
            # Check if we've reached the portal
            if (x, y) == goal:
                return True
                
            # Try all four directions
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                
                # Check if the new position is valid
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    cell = self.grid[nx][ny]
                    
                    # Can move to empty cells, safe paths, and the portal
                    if ((cell == CellType.EMPTY or cell == CellType.SAFE_PATH or cell == CellType.PORTAL) and 
                            (nx, ny) not in visited):
                        queue.append((nx, ny))
                        visited.add((nx, ny))
        
        # No path found
        return False
    
    def get_cell(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[x][y]
        return None
    
    def is_visible(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.visible_grid[x][y]
        return False
    
    def update_visibility(self, pulses):
        # Reset visibility
        self.visible_grid = [[False for _ in range(self.height)] for _ in range(self.width)]
        
        # Update visibility based on active pulses
        for pulse in pulses:
            if not pulse.active:
                continue
                
            # Calculate the maximum distance the pulse has traveled
            max_distance = pulse.radius / GRID_SIZE
            
            # Check cells within the pulse radius
            for x in range(max(0, int(pulse.x - max_distance)), min(self.width, int(pulse.x + max_distance + 1))):
                for y in range(max(0, int(pulse.y - max_distance)), min(self.height, int(pulse.y + max_distance + 1))):
                    # Calculate distance from pulse center to cell
                    distance = ((x - pulse.x) ** 2 + (y - pulse.y) ** 2) ** 0.5
                    
                    if distance <= max_distance:
                        cell_type = self.grid[x][y]
                        
                        # Red pulse reveals traps
                        if pulse.type == PulseType.RED and cell_type == CellType.TRAP:
                            self.visible_grid[x][y] = True
                        
                        # Green pulse reveals safe paths
                        elif pulse.type == PulseType.GREEN and cell_type == CellType.SAFE_PATH:
                            self.visible_grid[x][y] = True
                        
                        # Blue pulse reveals portals
                        elif pulse.type == PulseType.BLUE and cell_type == CellType.PORTAL:
                            self.visible_grid[x][y] = True
                        
                        # All pulses reveal walls
                        elif cell_type in [CellType.WALL, CellType.REFLECTIVE_WALL, CellType.ABSORBING_WALL, CellType.MOVING_WALL]:
                            self.visible_grid[x][y] = True
    
    def update_moving_walls(self, dt):
        new_moving_walls = []
        
        for x, y, direction in self.moving_walls:
            # Remove the wall from its current position
            self.grid[x][y] = CellType.EMPTY
            
            # Calculate new position
            dx, dy = direction.value
            new_x, new_y = x + dx, y + dy
            
            # Check if the new position is valid
            if (1 <= new_x < self.width - 1 and 1 <= new_y < self.height - 1 and 
                self.grid[new_x][new_y] == CellType.EMPTY):
                # Move the wall
                self.grid[new_x][new_y] = CellType.MOVING_WALL
                new_moving_walls.append((new_x, new_y, direction))
            else:
                # Change direction if blocked
                new_direction = random.choice(list(Direction))
                self.grid[x][y] = CellType.MOVING_WALL
                new_moving_walls.append((x, y, new_direction))
        
        self.moving_walls = new_moving_walls
    
    def draw(self, screen, camera_offset_x, camera_offset_y):
        for x in range(self.width):
            for y in range(self.height):
                cell_type = self.grid[x][y]
                is_visible = self.visible_grid[x][y]
                
                # Calculate screen position
                screen_x = x * GRID_SIZE - camera_offset_x
                screen_y = y * GRID_SIZE - camera_offset_y
                
                # Skip if outside screen
                if (screen_x + GRID_SIZE < 0 or screen_x > SCREEN_WIDTH or 
                    screen_y + GRID_SIZE < 0 or screen_y > SCREEN_HEIGHT):
                    continue
                
                # Draw cell based on type and visibility
                if cell_type == CellType.EMPTY:
                    # Draw grid lines
                    pygame.draw.rect(screen, GRAY, (screen_x, screen_y, GRID_SIZE, GRID_SIZE), 1)
                elif is_visible:
                    if cell_type == CellType.WALL:
                        pygame.draw.rect(screen, WHITE, (screen_x, screen_y, GRID_SIZE, GRID_SIZE))
                    elif cell_type == CellType.TRAP:
                        pygame.draw.rect(screen, RED, (screen_x, screen_y, GRID_SIZE, GRID_SIZE))
                    elif cell_type == CellType.SAFE_PATH:
                        pygame.draw.rect(screen, GREEN, (screen_x, screen_y, GRID_SIZE, GRID_SIZE))
                    elif cell_type == CellType.PORTAL:
                        pygame.draw.rect(screen, BLUE, (screen_x, screen_y, GRID_SIZE, GRID_SIZE))
                    elif cell_type == CellType.REFLECTIVE_WALL:
                        pygame.draw.rect(screen, (200, 200, 200), (screen_x, screen_y, GRID_SIZE, GRID_SIZE))
                    elif cell_type == CellType.ABSORBING_WALL:
                        pygame.draw.rect(screen, (50, 50, 50), (screen_x, screen_y, GRID_SIZE, GRID_SIZE))
                    elif cell_type == CellType.MOVING_WALL:
                        pygame.draw.rect(screen, (150, 100, 200), (screen_x, screen_y, GRID_SIZE, GRID_SIZE))
                else:
                    # Draw grid lines for unexplored areas
                    pygame.draw.rect(screen, GRAY, (screen_x, screen_y, GRID_SIZE, GRID_SIZE), 1)

class GameManager:
    def __init__(self):
        # Initialize display in fullscreen mode if enabled
        if FULLSCREEN:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            # Get the actual screen dimensions
            info = pygame.display.Info()
            global SCREEN_WIDTH, SCREEN_HEIGHT
            SCREEN_WIDTH = info.current_w
            SCREEN_HEIGHT = info.current_h
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            
        pygame.display.set_caption("Color Echo Maze")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 18)
        
        # Load sound effects
        self.load_sounds()
        
        self.level = 1
        self.maze_width = 20 + self.level * 2
        self.maze_height = 15 + self.level * 2
        
        # Calculate time limit based on level
        self.time_limit = self.calculate_time_limit()
        
        self.maze = Maze(self.maze_width, self.maze_height, self.level)
        self.player = Player(1, 1)
        self.pulses = []
        
        self.game_over = False
        self.level_complete = False
        self.time_expired = False  # New flag for time expiration
        self.start_time = time.time()
        self.elapsed_time = 0
        
        # Camera offset
        self.camera_offset_x = 0
        self.camera_offset_y = 0
    
    # Add this new method to calculate time limit based on level
    def calculate_time_limit(self):
        # Base time + additional time per level (30 seconds per level after level 1)
        return BASE_TIME_LIMIT + (self.level - 1) * 30
    
    def load_sounds(self):
        # Create a dictionary to store our sounds
        self.sounds = {}
        
        # Try to load each sound file, with error handling in case files don't exist
        try:
            self.sounds['move'] = pygame.mixer.Sound(SOUND_MOVE)
            self.sounds['red_pulse'] = pygame.mixer.Sound(SOUND_RED_PULSE)
            self.sounds['green_pulse'] = pygame.mixer.Sound(SOUND_GREEN_PULSE)
            self.sounds['blue_pulse'] = pygame.mixer.Sound(SOUND_BLUE_PULSE)
            self.sounds['game_over'] = pygame.mixer.Sound(SOUND_GAME_OVER)
            self.sounds['level_complete'] = pygame.mixer.Sound(SOUND_LEVEL_COMPLETE)
        except Exception as e:
            print(f"Warning: Could not load sound files. Error: {e}")
            # Create empty dictionary if sounds can't be loaded
            self.sounds = {}
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                
                # Toggle fullscreen with F11
                if event.key == pygame.K_F11:
                    global FULLSCREEN
                    FULLSCREEN = not FULLSCREEN
                    if FULLSCREEN:
                        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        info = pygame.display.Info()
                        global SCREEN_WIDTH, SCREEN_HEIGHT
                        SCREEN_WIDTH = info.current_w
                        SCREEN_HEIGHT = info.current_h
                    else:
                        SCREEN_WIDTH = 800
                        SCREEN_HEIGHT = 600
                        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                
                # Player movement
                if not self.game_over and not self.level_complete and not self.time_expired:
                    moved = False
                    if event.key == pygame.K_UP:
                        moved = self.player.move(Direction.UP, self.maze)
                    elif event.key == pygame.K_DOWN:
                        moved = self.player.move(Direction.DOWN, self.maze)
                    elif event.key == pygame.K_LEFT:
                        moved = self.player.move(Direction.LEFT, self.maze)
                    elif event.key == pygame.K_RIGHT:
                        moved = self.player.move(Direction.RIGHT, self.maze)
                    
                    # Play movement sound if player moved
                    if moved and 'move' in self.sounds:
                        self.sounds['move'].play()
                    
                    # Manual pulse emission (still available but not necessary with auto pulses)
                    if event.key == pygame.K_r:
                        pulse = self.player.emit_pulse(PulseType.RED, self.maze)
                        if pulse:
                            self.pulses.append(pulse)
                            # Play red pulse sound
                            if 'red_pulse' in self.sounds:
                                self.sounds['red_pulse'].play()
                    elif event.key == pygame.K_g:
                        pulse = self.player.emit_pulse(PulseType.GREEN, self.maze)
                        if pulse:
                            self.pulses.append(pulse)
                            # Play green pulse sound
                            if 'green_pulse' in self.sounds:
                                self.sounds['green_pulse'].play()
                    elif event.key == pygame.K_b:
                        pulse = self.player.emit_pulse(PulseType.BLUE, self.maze)
                        if pulse:
                            self.pulses.append(pulse)
                            # Play blue pulse sound
                            if 'blue_pulse' in self.sounds:
                                self.sounds['blue_pulse'].play()
                
                # Restart level if game over or time expired
                if (self.game_over or self.time_expired) and event.key == pygame.K_SPACE:
                    self.restart_level()
                
                # Next level if level complete
                if self.level_complete and event.key == pygame.K_SPACE:
                    self.next_level()
        
        return True
    
    def update(self, dt):
        if self.game_over or self.level_complete or self.time_expired:
            return
        
        # Update elapsed time
        self.elapsed_time = time.time() - self.start_time
        
        # Check if time limit has expired
        if self.elapsed_time >= self.time_limit:
            self.time_expired = True
            # Play game over sound
            if 'game_over' in self.sounds:
                self.sounds['game_over'].play()
            return
        
        # Update player energy
        self.player.regenerate_energy(dt)
        
        # Handle automated pulse emission
        pulse, pulse_type = self.player.auto_emit_pulse(time.time(), self.maze)
        if pulse:
            self.pulses.append(pulse)
            # Play appropriate sound
            if pulse_type == PulseType.RED and 'red_pulse' in self.sounds:
                self.sounds['red_pulse'].play()
            elif pulse_type == PulseType.GREEN and 'green_pulse' in self.sounds:
                self.sounds['green_pulse'].play()
            elif pulse_type == PulseType.BLUE and 'blue_pulse' in self.sounds:
                self.sounds['blue_pulse'].play()
        
        # Update pulses
        active_pulses = []
        for pulse in self.pulses:
            pulse.update(dt)
            if pulse.active:
                active_pulses.append(pulse)
        self.pulses = active_pulses
        
        # Update maze visibility based on pulses
        self.maze.update_visibility(self.pulses)
        
        # Update moving walls (every 1 second)
        if int(self.elapsed_time) % 1 == 0:
            self.maze.update_moving_walls(dt)
        
        # Check for collisions
        cell = self.maze.get_cell(self.player.x, self.player.y)
        if cell == CellType.TRAP:
            self.game_over = True
            # Play game over sound
            if 'game_over' in self.sounds:
                self.sounds['game_over'].play()
        elif cell == CellType.PORTAL:
            self.level_complete = True
            # Play level complete sound
            if 'level_complete' in self.sounds:
                self.sounds['level_complete'].play()
        
        # Update camera to follow player
        target_camera_x = self.player.x * GRID_SIZE - SCREEN_WIDTH // 2
        target_camera_y = self.player.y * GRID_SIZE - SCREEN_HEIGHT // 2
        
        # Smooth camera movement
        self.camera_offset_x += (target_camera_x - self.camera_offset_x) * 5 * dt
        self.camera_offset_y += (target_camera_y - self.camera_offset_y) * 5 * dt
        
        # Clamp camera to maze bounds
        self.camera_offset_x = max(0, min(self.camera_offset_x, self.maze.width * GRID_SIZE - SCREEN_WIDTH))
        self.camera_offset_y = max(0, min(self.camera_offset_y, self.maze.height * GRID_SIZE - SCREEN_HEIGHT))


    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw maze
        self.maze.draw(self.screen, self.camera_offset_x, self.camera_offset_y)
        
        # Draw pulses
        for pulse in self.pulses:
            pulse.draw(self.screen, self.camera_offset_x, self.camera_offset_y)
        
        # Draw player
        self.player.draw(self.screen, self.camera_offset_x, self.camera_offset_y)
        
        # Draw HUD
        self.draw_hud()
        
        # Draw game over, level complete, or time expired message
        if self.game_over:
            self.draw_message("Game Over! Press SPACE to restart", RED)
        elif self.time_expired:
            self.draw_message("Time's Up! Press SPACE to restart", RED)
        elif self.level_complete:
            self.draw_message("Level Complete! Press SPACE for next level", GREEN)
        
        pygame.display.flip()
    
    def draw_hud(self):
        # Calculate scaling factors for HUD elements based on screen size
        scale_factor = min(SCREEN_WIDTH / 800, SCREEN_HEIGHT / 600)
        bar_width = int(150 * scale_factor)
        bar_height = int(20 * scale_factor)
        padding = int(10 * scale_factor)
        
        # Adjust font sizes based on screen resolution
        if not hasattr(self, 'scaled_font'):
            font_size = int(24 * scale_factor)
            small_font_size = int(18 * scale_factor)
            self.scaled_font = pygame.font.SysFont('Arial', font_size)
            self.scaled_small_font = pygame.font.SysFont('Arial', small_font_size)
        
        # Red pulse energy
        pygame.draw.rect(self.screen, (50, 0, 0), (padding, padding, bar_width, bar_height))
        pygame.draw.rect(self.screen, RED, (padding, padding, int(bar_width * self.player.pulse_energy[PulseType.RED] / 100), bar_height))
        red_text = self.scaled_small_font.render(f"Red (R): {int(self.player.pulse_energy[PulseType.RED])}%", True, WHITE)
        self.screen.blit(red_text, (padding + 5, padding + 2))
        
        # Green pulse energy
        pygame.draw.rect(self.screen, (0, 50, 0), (padding, padding * 2 + bar_height, bar_width, bar_height))
        pygame.draw.rect(self.screen, GREEN, (padding, padding * 2 + bar_height, int(bar_width * self.player.pulse_energy[PulseType.GREEN] / 100), bar_height))
        green_text = self.scaled_small_font.render(f"Green (G): {int(self.player.pulse_energy[PulseType.GREEN])}%", True, WHITE)
        self.screen.blit(green_text, (padding + 5, padding * 2 + bar_height + 2))
        
        # Blue pulse energy
        pygame.draw.rect(self.screen, (0, 0, 50), (padding, padding * 3 + bar_height * 2, bar_width, bar_height))
        pygame.draw.rect(self.screen, BLUE, (padding, padding * 3 + bar_height * 2, int(bar_width * self.player.pulse_energy[PulseType.BLUE] / 100), bar_height))
        blue_text = self.scaled_small_font.render(f"Blue (B): {int(self.player.pulse_energy[PulseType.BLUE])}%", True, WHITE)
        self.screen.blit(blue_text, (padding + 5, padding * 3 + bar_height * 2 + 2))
        
        # Level and time
        level_text = self.scaled_font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (SCREEN_WIDTH - level_text.get_width() - padding, padding))
        
        # Show time remaining instead of elapsed time
        time_remaining = max(0, self.time_limit - self.elapsed_time)
        time_color = WHITE
        if time_remaining < 30:  # Turn red when less than 30 seconds remain
            time_color = RED
        time_text = self.scaled_font.render(f"Time: {int(time_remaining)}s", True, time_color)
        self.screen.blit(time_text, (SCREEN_WIDTH - time_text.get_width() - padding, padding * 2 + level_text.get_height()))
        
        # Auto-pulse timer
        next_pulse_in = max(0, AUTO_PULSE_INTERVAL - (time.time() - self.player.last_auto_pulse_time))
        pulse_timer_text = self.scaled_small_font.render(f"Next pulse in: {next_pulse_in:.1f}s", True, WHITE)
        self.screen.blit(pulse_timer_text, (SCREEN_WIDTH - pulse_timer_text.get_width() - padding, 
                                        padding * 3 + level_text.get_height() + time_text.get_height()))
        
        # Legend
        legend_y = SCREEN_HEIGHT - int(120 * scale_factor)  # Moved up to make room for instructions
        legend_text = self.scaled_small_font.render("Legend:", True, WHITE)
        self.screen.blit(legend_text, (padding, legend_y))
        
        legend_box_size = int(15 * scale_factor)
        legend_spacing = int(20 * scale_factor)
        
        pygame.draw.rect(self.screen, RED, (padding, legend_y + legend_spacing, legend_box_size, legend_box_size))
        red_legend = self.scaled_small_font.render("Red (R): Reveals traps", True, WHITE)
        self.screen.blit(red_legend, (padding + legend_box_size + 5, legend_y + legend_spacing))
        
        pygame.draw.rect(self.screen, GREEN, (padding, legend_y + legend_spacing * 2, legend_box_size, legend_box_size))
        green_legend = self.scaled_small_font.render("Green (G): Reveals safe paths", True, WHITE)
        self.screen.blit(green_legend, (padding + legend_box_size + 5, legend_y + legend_spacing * 2))
        
        pygame.draw.rect(self.screen, BLUE, (padding, legend_y + legend_spacing * 3, legend_box_size, legend_box_size))
        blue_legend = self.scaled_small_font.render("Blue (B): Reveals portals", True, WHITE)
        self.screen.blit(blue_legend, (padding + legend_box_size + 5, legend_y + legend_spacing * 3))
        
        # Instructions
        instructions = self.scaled_small_font.render("Arrow Keys: Move | Auto-pulses every 4s | Find the blue portal within time limit", True, WHITE)
        self.screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, SCREEN_HEIGHT - padding * 2))
    
    def draw_message(self, message, color):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # Scale message font based on screen size
        scale_factor = min(SCREEN_WIDTH / 800, SCREEN_HEIGHT / 600)
        font_size = int(32 * scale_factor)  # Larger font for messages
        message_font = pygame.font.SysFont('Arial', font_size)
        
        text = message_font.render(message, True, color)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)
    
    def restart_level(self):
        # Keep the current screen mode when restarting
        self.maze = Maze(self.maze_width, self.maze_height, self.level)
        self.player = Player(1, 1)
        self.pulses = []
        self.game_over = False
        self.level_complete = False
        self.time_expired = False
        self.start_time = time.time()
        self.elapsed_time = 0
        
        # Recalculate time limit for current level
        self.time_limit = self.calculate_time_limit()
    
    def next_level(self):
        # Keep the current screen mode when advancing to next level
        self.level += 1
        self.maze_width = 20 + self.level * 2
        self.maze_height = 15 + self.level * 2
        self.maze = Maze(self.maze_width, self.maze_height, self.level)
        self.player = Player(1, 1)
        self.pulses = []
        self.game_over = False
        self.level_complete = False
        self.time_expired = False
        self.start_time = time.time()
        self.elapsed_time = 0
        
        # Calculate new time limit for the next level
        self.time_limit = self.calculate_time_limit()
    
    def run(self):
        last_time = time.time()
        
        while True:
            # Calculate delta time
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            # Handle events
            if not self.handle_events():
                break
            
            # Update game state
            self.update(dt)
            
            # Draw everything
            self.draw()
            
            # Cap the frame rate
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = GameManager()
    game.run()