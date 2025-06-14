import pygame
import random
from typing import Tuple

class SpriteGenerator:
    """Generates procedural pixel sprites for entities"""
    
    def __init__(self, size: int = 16):
        self.size = size
        self.colors = {
            'skin': [(255, 218, 185), (240, 200, 160), (210, 180, 140), (180, 150, 120)],
            'hair': [(50, 30, 15), (139, 69, 19), (160, 120, 80), (255, 215, 0)],
            'clothes': [(65, 105, 225), (46, 139, 87), (178, 34, 34), (148, 0, 211)]
        }

    def generate_sprite(self, seed: int = None) -> pygame.Surface:
        """Generate a unique pixel sprite based on a seed"""
        if seed is not None:
            random.seed(seed)
            
        # Create surface with alpha channel
        sprite = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # Generate base shape (body)
        skin_color = random.choice(self.colors['skin'])
        self._generate_body(sprite, skin_color)
        
        # Add features (hair, clothes)
        hair_color = random.choice(self.colors['hair'])
        clothes_color = random.choice(self.colors['clothes'])
        self._add_features(sprite, hair_color, clothes_color)
        
        if seed is not None:
            random.seed()  # Reset random seed
            
        return sprite

    def _generate_body(self, surface: pygame.Surface, color: Tuple[int, int, int]) -> None:
        """Generate the basic body shape"""
        # Generate a symmetrical pattern for the body
        pattern = []
        half_width = self.size // 2
        
        for y in range(self.size):
            row = []
            for x in range(half_width):
                if random.random() > 0.5:
                    row.append(1)
                else:
                    row.append(0)
            # Mirror the pattern
            full_row = row + row[::-1]
            pattern.append(full_row)
        
        # Apply the pattern
        for y in range(self.size):
            for x in range(self.size):
                if pattern[y][x]:
                    surface.set_at((x, y), color)

    def _add_features(self, surface: pygame.Surface, 
                     hair_color: Tuple[int, int, int],
                     clothes_color: Tuple[int, int, int]) -> None:
        """Add distinguishing features to the sprite"""
        # Add hair (top 1/4 of sprite)
        hair_height = self.size // 4
        for y in range(hair_height):
            for x in range(self.size):
                if random.random() > 0.3:  # 70% chance of hair pixel
                    surface.set_at((x, y), hair_color)
        
        # Add clothes (bottom 1/3 of sprite)
        clothes_start = int(self.size * 0.66)
        for y in range(clothes_start, self.size):
            for x in range(self.size):
                if surface.get_at((x, y))[3] > 0:  # If pixel is not transparent
                    surface.set_at((x, y), clothes_color)

    def generate_animation_frames(self, base_sprite: pygame.Surface, 
                                num_frames: int = 4) -> list[pygame.Surface]:
        """Generate animation frames from a base sprite"""
        frames = [base_sprite]
        
        for _ in range(num_frames - 1):
            frame = base_sprite.copy()
            # Add slight variations for animation
            for y in range(self.size):
                for x in range(self.size):
                    if frame.get_at((x, y))[3] > 0:  # If pixel is not transparent
                        if random.random() > 0.9:  # 10% chance to modify pixel
                            # Shift pixel slightly
                            if x + 1 < self.size:
                                color = frame.get_at((x, y))
                                frame.set_at((x + 1, y), color)
                                frame.set_at((x, y), (0, 0, 0, 0))
            frames.append(frame)
        
        return frames
