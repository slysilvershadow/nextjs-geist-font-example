import math
import random
from typing import Dict, List, Optional, Tuple, Any
import pygame
import numpy as np

class Point:
    """2D point with utility methods"""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def distance_to(self, other: 'Point') -> float:
        """Calculate Euclidean distance to another point"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def manhattan_distance_to(self, other: 'Point') -> float:
        """Calculate Manhattan distance to another point"""
        return abs(self.x - other.x) + abs(self.y - other.y)
    
    def direction_to(self, other: 'Point') -> Tuple[float, float]:
        """Get normalized direction vector to another point"""
        dx = other.x - self.x
        dy = other.y - self.y
        length = math.sqrt(dx*dx + dy*dy)
        if length == 0:
            return (0, 0)
        return (dx/length, dy/length)

class PathFinder:
    """A* pathfinding implementation"""
    def __init__(self, world_width: int, world_height: int):
        self.width = world_width
        self.height = world_height
        
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int],
                  is_walkable: callable) -> Optional[List[Tuple[int, int]]]:
        """
        Find a path between start and goal positions
        
        Args:
            start: Starting (x, y) position
            goal: Target (x, y) position
            is_walkable: Function that takes (x, y) and returns if position is walkable
        
        Returns:
            List of positions forming the path, or None if no path exists
        """
        if not is_walkable(goal[0], goal[1]):
            return None
            
        # Initialize data structures
        frontier = [(0, start)]  # Priority queue of (priority, position)
        came_from = {start: None}
        cost_so_far = {start: 0}
        
        while frontier:
            current = frontier.pop(0)[1]
            
            if current == goal:
                break
                
            # Check all neighbors
            for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                next_pos = (current[0] + dx, current[1] + dy)
                
                # Skip if out of bounds or unwalkable
                if (not (0 <= next_pos[0] < self.width and 
                        0 <= next_pos[1] < self.height) or
                    not is_walkable(next_pos[0], next_pos[1])):
                    continue
                
                # Calculate new cost
                new_cost = cost_so_far[current] + 1
                
                if (next_pos not in cost_so_far or 
                    new_cost < cost_so_far[next_pos]):
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + self._heuristic(next_pos, goal)
                    frontier.append((priority, next_pos))
                    frontier.sort()  # Keep frontier sorted by priority
                    came_from[next_pos] = current
        
        # Reconstruct path
        if goal not in came_from:
            return None
            
        path = []
        current = goal
        while current is not None:
            path.append(current)
            current = came_from[current]
        path.reverse()
        
        return path
    
    def _heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        """Manhattan distance heuristic"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

class NoiseGenerator:
    """Perlin noise generator for terrain generation"""
    def __init__(self, seed: Optional[int] = None):
        self.seed = seed if seed is not None else random.randint(0, 1000000)
        random.seed(self.seed)
        
        # Generate permutation table
        self.perm = list(range(256))
        random.shuffle(self.perm)
        self.perm += self.perm
    
    def noise2d(self, x: float, y: float) -> float:
        """Generate 2D Perlin noise value"""
        # Integer coordinates
        xi = int(x) & 255
        yi = int(y) & 255
        
        # Decimal parts
        xf = x - int(x)
        yf = y - int(y)
        
        # Fade functions
        u = self._fade(xf)
        v = self._fade(yf)
        
        # Hash coordinates
        aa = self.perm[self.perm[xi] + yi]
        ab = self.perm[self.perm[xi] + yi + 1]
        ba = self.perm[self.perm[xi + 1] + yi]
        bb = self.perm[self.perm[xi + 1] + yi + 1]
        
        # Blend results
        x1 = self._lerp(
            self._grad(aa, xf, yf),
            self._grad(ba, xf - 1, yf),
            u
        )
        x2 = self._lerp(
            self._grad(ab, xf, yf - 1),
            self._grad(bb, xf - 1, yf - 1),
            u
        )
        
        return (self._lerp(x1, x2, v) + 1) / 2
    
    def _fade(self, t: float) -> float:
        """Fade function for smooth interpolation"""
        return t * t * t * (t * (t * 6 - 15) + 10)
    
    def _lerp(self, a: float, b: float, t: float) -> float:
        """Linear interpolation"""
        return a + t * (b - a)
    
    def _grad(self, hash: int, x: float, y: float) -> float:
        """Gradient function"""
        h = hash & 15
        grad_x = 1 + (h & 7)  # Gradient x
        grad_y = 1 + (h >> 4)  # Gradient y
        return ((grad_x * x + grad_y * y) * (1 if (h & 8) == 0 else -1))

def load_sprite_sheet(path: str, sprite_width: int, sprite_height: int) -> List[pygame.Surface]:
    """Load a sprite sheet and split into individual sprites"""
    try:
        sheet = pygame.image.load(path).convert_alpha()
        sprites = []
        
        for y in range(0, sheet.get_height(), sprite_height):
            for x in range(0, sheet.get_width(), sprite_width):
                sprite = pygame.Surface((sprite_width, sprite_height), 
                                     pygame.SRCALPHA)
                sprite.blit(sheet, (0, 0), (x, y, sprite_width, sprite_height))
                sprites.append(sprite)
        
        return sprites
    except pygame.error as e:
        print(f"Error loading sprite sheet {path}: {e}")
        return []

def draw_text(surface: pygame.Surface, text: str, pos: Tuple[int, int],
              color: Tuple[int, int, int], font_size: int = 20,
              centered: bool = False) -> None:
    """Draw text on a surface with optional centering"""
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    
    if centered:
        pos = (pos[0] - text_surface.get_width()//2,
               pos[1] - text_surface.get_height()//2)
    
    surface.blit(text_surface, pos)

def create_color_gradient(color1: Tuple[int, int, int],
                         color2: Tuple[int, int, int],
                         steps: int) -> List[Tuple[int, int, int]]:
    """Create a gradient between two colors"""
    gradient = []
    for i in range(steps):
        ratio = i / (steps - 1)
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        gradient.append((r, g, b))
    return gradient

def interpolate_value(value: float, old_min: float, old_max: float,
                     new_min: float, new_max: float) -> float:
    """Interpolate a value from one range to another"""
    # Avoid division by zero
    if old_max == old_min:
        return new_min
    
    ratio = (value - old_min) / (old_max - old_min)
    return new_min + ratio * (new_max - new_min)

def calculate_line_of_sight(start: Tuple[int, int], end: Tuple[int, int],
                          is_blocking: callable) -> bool:
    """
    Calculate if there is line of sight between two points
    
    Args:
        start: Starting (x, y) position
        end: Ending (x, y) position
        is_blocking: Function that takes (x, y) and returns if position blocks sight
    
    Returns:
        True if there is line of sight, False otherwise
    """
    x1, y1 = start
    x2, y2 = end
    
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    
    x = x1
    y = y1
    
    n = 1 + dx + dy
    x_inc = 1 if x2 > x1 else -1
    y_inc = 1 if y2 > y1 else -1
    
    error = dx - dy
    dx *= 2
    dy *= 2
    
    for _ in range(n):
        if is_blocking(x, y):
            return False
            
        if error > 0:
            x += x_inc
            error -= dy
        else:
            y += y_inc
            error += dx
    
    return True

def generate_unique_id() -> str:
    """Generate a unique identifier"""
    return f"{random.getrandbits(32):08x}"

def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp a value between min and max"""
    return max(min_value, min(max_value, value))

def distance_between(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two positions"""
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def angle_between(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
    """Calculate angle in radians between two positions"""
    return math.atan2(pos2[1] - pos1[1], pos2[0] - pos1[0])

def rotate_point(point: Tuple[float, float], center: Tuple[float, float],
                angle: float) -> Tuple[float, float]:
    """Rotate a point around a center by an angle (in radians)"""
    s = math.sin(angle)
    c = math.cos(angle)
    
    # Translate point back to origin
    px = point[0] - center[0]
    py = point[1] - center[1]
    
    # Rotate point
    xnew = px * c - py * s
    ynew = px * s + py * c
    
    # Translate point back
    return (xnew + center[0], ynew + center[1])

def smooth_value(current: float, target: float, smoothing: float) -> float:
    """Smoothly interpolate between current and target value"""
    return current + (target - current) * clamp(smoothing, 0, 1)

def format_time(minutes: int) -> str:
    """Format minutes into HH:MM string"""
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"

def chance(probability: float) -> bool:
    """Return True with given probability (0-1)"""
    return random.random() < probability

def weighted_choice(choices: List[Any], weights: List[float]) -> Any:
    """Make a weighted random choice from a list"""
    total = sum(weights)
    r = random.uniform(0, total)
    upto = 0
    
    for choice, weight in zip(choices, weights):
        if upto + weight >= r:
            return choice
        upto += weight
    
    return choices[-1]  # Fallback to last choice

def create_circular_mask(size: int) -> pygame.Surface:
    """Create a circular alpha mask"""
    mask = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), 
                      (size//2, size//2), size//2)
    return mask
