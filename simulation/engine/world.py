import numpy as np
from typing import Dict, List, Tuple
import pygame
from .config import Config

class World:
    """
    Handles world generation and management including terrain, biomes, and resources.
    Uses layered noise for realistic terrain generation and biome distribution.
    """
    def __init__(self, config: Config):
        self.config = config
        
        # Initialize world arrays
        self.width = config.WORLD.WORLD_WIDTH
        self.height = config.WORLD.WORLD_HEIGHT
        
        # Terrain layers
        self.elevation = np.zeros((self.height, self.width))
        self.temperature = np.zeros((self.height, self.width))
        self.moisture = np.zeros((self.height, self.width))
        self.biomes = np.zeros((self.height, self.width), dtype=np.int32)
        self.resources = np.zeros((self.height, self.width), dtype=np.int32)
        
        # Resource tracking
        self.resource_locations = {}  # Dict to track resource positions
        
        # Generate initial world
        self._generate_world()

    def _generate_world(self) -> None:
        """Generate the complete world using a series of noise layers and algorithms"""
        self._generate_elevation()
        self._generate_temperature()
        self._generate_moisture()
        self._determine_biomes()
        self._place_resources()

    def _generate_elevation(self) -> None:
        """Generate elevation using multiple octaves of Perlin noise"""
        scale = 50.0
        octaves = 6
        persistence = 0.5
        lacunarity = 2.0
        
        # Generate raw elevation values
        raw_elevation = np.zeros((self.height, self.width))
        for y in range(self.height):
            for x in range(self.width):
                elevation = 0
                amplitude = 1.0
                frequency = 1.0
                max_value = 0
                
                for i in range(octaves):
                    sample_x = x / scale * frequency
                    sample_y = y / scale * frequency
                    
                    # Use numpy's random instead of noise library for simplicity
                    elevation += self._get_noise(sample_x, sample_y) * amplitude
                    
                    max_value += amplitude
                    amplitude *= persistence
                    frequency *= lacunarity
                
                raw_elevation[y, x] = elevation / max_value
        
        # Normalize elevation values to [0, 1] range
        min_elevation = np.min(raw_elevation)
        max_elevation = np.max(raw_elevation)
        self.elevation = (raw_elevation - min_elevation) / (max_elevation - min_elevation)

    def _generate_temperature(self) -> None:
        """Generate temperature based on elevation and latitude"""
        for y in range(self.height):
            base_temp = 1.0 - abs(y - self.height/2) / (self.height/2)  # Latitude effect
            for x in range(self.width):
                # Temperature decreases with elevation
                elevation_factor = 1.0 - self.elevation[y, x]
                self.temperature[y, x] = base_temp * elevation_factor

    def _generate_moisture(self) -> None:
        """Generate moisture levels using noise and elevation data"""
        scale = 30.0
        for y in range(self.height):
            for x in range(self.width):
                base_moisture = self._get_noise(x/scale, y/scale)
                # Moisture tends to collect in lower elevations
                elevation_factor = 1.0 - self.elevation[y, x]
                self.moisture[y, x] = (base_moisture + elevation_factor) / 2

    def _determine_biomes(self) -> None:
        """Determine biomes based on temperature, moisture, and elevation"""
        for y in range(self.height):
            for x in range(self.width):
                temp = self.temperature[y, x]
                moisture = self.moisture[y, x]
                elevation = self.elevation[y, x]
                
                # Convert to actual temperature range
                actual_temp = self.config.WORLD.MIN_TEMPERATURE + \
                            temp * (self.config.WORLD.MAX_TEMPERATURE - 
                                  self.config.WORLD.MIN_TEMPERATURE)
                
                # Find matching biome
                for biome_name, thresholds in self.config.BIOME_THRESHOLDS.items():
                    temp_range = thresholds["temp"]
                    moisture_range = thresholds["moisture"]
                    elevation_range = thresholds["elevation"]
                    
                    if (temp_range[0] <= actual_temp <= temp_range[1] and
                        moisture_range[0] <= moisture <= moisture_range[1] and
                        elevation_range[0] <= elevation * 3000 <= elevation_range[1]):
                        self.biomes[y, x] = list(self.config.BIOME_THRESHOLDS.keys()).index(biome_name)
                        break

    def _place_resources(self) -> None:
        """Place resources throughout the world based on biome types"""
        self.resource_locations.clear()
        
        # Define resource types as enum values
        RESOURCE_TYPES = [
            "TREE", "BUSH", "HERB", "STONE", "METAL", "GEMSTONE",
            "VEGETABLE", "MINERAL", "FISH", "SHELL", "CORAL"
        ]
        
        # Define resource placement rules based on biomes
        resource_rules = {
            "FOREST": ["TREE", "BUSH", "HERB"],
            "MOUNTAIN": ["STONE", "METAL", "GEMSTONE"],
            "PLAINS": ["BUSH", "HERB", "VEGETABLE"],
            "DESERT": ["STONE", "MINERAL"],
            "WATER": ["FISH", "SHELL", "CORAL"]
        }
        
        # Place resources according to rules
        for y in range(self.height):
            for x in range(self.width):
                biome_name = list(self.config.BIOME_THRESHOLDS.keys())[self.biomes[y, x]]
                biome_type = next((k for k in resource_rules.keys() 
                                 if any(b in biome_name for b in k.split('_'))), None)
                
                if biome_type and np.random.random() < 0.1:  # 10% chance of resource
                    resource = np.random.choice(resource_rules[biome_type])
                    self.resources[y, x] = RESOURCE_TYPES.index(resource)
                    self.resource_locations[(x, y)] = resource

    def _get_noise(self, x: float, y: float) -> float:
        """Simple noise function for demonstration"""
        # This is a very basic noise implementation
        # In a real implementation, you'd want to use a proper noise library
        return (np.sin(x) + np.cos(y)) / 2 + 0.5

    def get_biome_at(self, x: int, y: int) -> str:
        """Get the biome type at the given coordinates"""
        if 0 <= x < self.width and 0 <= y < self.height:
            biome_index = self.biomes[y, x]
            return list(self.config.BIOME_THRESHOLDS.keys())[biome_index]
        return "NONE"

    def get_resource_at(self, x: int, y: int) -> str:
        """Get the resource type at the given coordinates"""
        return self.resource_locations.get((x, y), "NONE")

    def update(self, current_time) -> None:
        """Update world state based on time (weather, resource regeneration, etc.)"""
        # TODO: Implement weather system
        # TODO: Implement resource regeneration
        pass

    def render(self, screen: pygame.Surface, visible_area: pygame.Rect,
              zoom_level: float, camera_x: float, camera_y: float) -> None:
        """Render the visible portion of the world"""
        tile_size = int(self.config.WORLD.TILE_SIZE * zoom_level)
        
        # Calculate visible range
        start_x = max(0, int(camera_x))
        start_y = max(0, int(camera_y))
        end_x = min(self.width, int(camera_x + visible_area.width + 1))
        end_y = min(self.height, int(camera_y + visible_area.height + 1))
        
        # Render terrain and biomes
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                screen_x = int((x - camera_x) * tile_size)
                screen_y = int((y - camera_y) * tile_size)
                
                # Skip if outside screen
                if (screen_x + tile_size < 0 or screen_x >= self.config.DISPLAY.SCREEN_WIDTH or
                    screen_y + tile_size < 0 or screen_y >= self.config.DISPLAY.SCREEN_HEIGHT):
                    continue
                
                # Get biome color
                biome_index = self.biomes[y, x]
                color = self._get_biome_color(biome_index)
                
                # Draw terrain tile
                pygame.draw.rect(screen, color, 
                               (screen_x, screen_y, tile_size, tile_size))
                
                # Draw resource if present
                if (x, y) in self.resource_locations:
                    resource_color = (139, 69, 19)  # Brown
                    pygame.draw.circle(screen, resource_color,
                                    (screen_x + tile_size//2,
                                     screen_y + tile_size//2),
                                    tile_size//4)

    def _get_biome_color(self, biome_index: int) -> Tuple[int, int, int]:
        """Get the color for a specific biome type"""
        # Define colors for each biome type
        colors = {
            "BOREAL_FOREST": (34, 139, 34),      # Forest Green
            "DECIDUOUS_FOREST": (0, 100, 0),      # Dark Green
            "RAINFOREST": (0, 128, 0),           # Green
            "TUNDRA": (238, 233, 233),          # Snow White
            "STEPPE": (218, 165, 32),           # Golden Rod
            "SAVANNA": (255, 228, 181),         # Moccasin
            "POLAR_DESERT": (255, 250, 250),    # Snow
            "SEMI_ARID_DESERT": (210, 180, 140), # Tan
            "SAND_DESERT": (244, 164, 96),      # Sandy Brown
            "HEATH": (85, 107, 47),             # Dark Olive Green
            "CHAPARRAL": (189, 183, 107),       # Dark Khaki
            "SWAMP": (47, 79, 79),              # Dark Slate Gray
        }
        
        biome_name = list(self.config.BIOME_THRESHOLDS.keys())[biome_index]
        return colors.get(biome_name, (128, 128, 128))  # Default gray if not found
