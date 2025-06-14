import pygame
from typing import Dict, List, Optional
from .config import Config
from .world import World
from .time_system import TimeSystem
from .entity_manager import EntityManager
from .resource_manager import ResourceManager

class Game:
    """
    Main game class that coordinates all simulation systems and manages the game state.
    """
    def __init__(self, screen: pygame.Surface, config: Config):
        self.screen = screen
        self.config = config
        
        # Initialize core systems
        self.time_system = TimeSystem(config)
        self.world = World(config)
        self.entity_manager = EntityManager(config)
        self.resource_manager = ResourceManager(config)
        
        # Game state flags
        self.paused = False
        self.debug_mode = False
        self.selected_entity = None
        
        # Camera/View settings
        self.camera_x = 0
        self.camera_y = 0
        self.zoom_level = config.DISPLAY.DEFAULT_ZOOM
        
        # Initialize clock for FPS tracking
        self.clock = pygame.time.Clock()

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events for user input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.paused = not self.paused
            elif event.key == pygame.K_d:
                self.debug_mode = not self.debug_mode
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                self._adjust_zoom(1)  # Zoom in
            elif event.key == pygame.K_MINUS:
                self._adjust_zoom(-1)  # Zoom out
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Handle entity selection
            mouse_pos = pygame.mouse.get_pos()
            world_pos = self._screen_to_world_pos(mouse_pos)
            self.selected_entity = self.entity_manager.get_entity_at_position(world_pos)

    def update(self) -> None:
        """Update game state for the current frame"""
        if not self.paused:
            # Update time system first as it affects all other systems
            self.time_system.update()
            
            # Update world state (environment, weather, etc.)
            self.world.update(self.time_system.current_time)
            
            # Update all entities (AI, movement, actions)
            self.entity_manager.update(
                self.time_system.current_time,
                self.world,
                self.resource_manager
            )
            
            # Update resources (regeneration, depletion)
            self.resource_manager.update(
                self.time_system.current_time,
                self.world
            )

    def render(self) -> None:
        """Render the current game state to the screen"""
        # Clear the screen
        self.screen.fill((0, 0, 0))
        
        # Calculate visible area based on camera position and zoom
        visible_area = self._get_visible_area()
        
        # Render world (terrain, resources)
        self.world.render(
            self.screen,
            visible_area,
            self.zoom_level,
            self.camera_x,
            self.camera_y
        )
        
        # Render entities
        self.entity_manager.render(
            self.screen,
            visible_area,
            self.zoom_level,
            self.camera_x,
            self.camera_y
        )
        
        # Render UI elements
        self._render_ui()
        
        if self.debug_mode:
            self._render_debug_info()

    def _adjust_zoom(self, direction: int) -> None:
        """Adjust zoom level within configured bounds"""
        current_index = self.config.DISPLAY.ZOOM_LEVELS.index(self.zoom_level)
        new_index = max(0, min(
            current_index + direction,
            len(self.config.DISPLAY.ZOOM_LEVELS) - 1
        ))
        self.zoom_level = self.config.DISPLAY.ZOOM_LEVELS[new_index]

    def _get_visible_area(self) -> pygame.Rect:
        """Calculate the visible area in world coordinates"""
        screen_width = self.config.SCREEN_WIDTH
        screen_height = self.config.SCREEN_HEIGHT
        
        # Convert screen dimensions to world coordinates
        visible_width = screen_width / (self.zoom_level * self.config.WORLD.TILE_SIZE)
        visible_height = screen_height / (self.zoom_level * self.config.WORLD.TILE_SIZE)
        
        return pygame.Rect(
            self.camera_x,
            self.camera_y,
            visible_width,
            visible_height
        )

    def _screen_to_world_pos(self, screen_pos: tuple) -> tuple:
        """Convert screen coordinates to world coordinates"""
        world_x = (screen_pos[0] / (self.zoom_level * self.config.WORLD.TILE_SIZE)) + self.camera_x
        world_y = (screen_pos[1] / (self.zoom_level * self.config.WORLD.TILE_SIZE)) + self.camera_y
        return (world_x, world_y)

    def _render_ui(self) -> None:
        """Render UI elements like time, selected entity info, etc."""
        # Render time
        time_text = self.time_system.get_time_string()
        font = pygame.font.Font(None, 36)
        text_surface = font.render(time_text, True, (255, 255, 255))
        self.screen.blit(text_surface, (10, 10))
        
        # Render selected entity info if any
        if self.selected_entity:
            self._render_entity_info(self.selected_entity)

    def _render_entity_info(self, entity) -> None:
        """Render detailed information about the selected entity"""
        font = pygame.font.Font(None, 24)
        y_offset = 50
        
        info_lines = [
            f"Name: {entity.name}",
            f"Health: {entity.needs['HEALTH']:.1f}",
            f"Energy: {entity.needs['ENERGY']:.1f}",
            f"Current Task: {entity.current_task}",
        ]
        
        for line in info_lines:
            text_surface = font.render(line, True, (255, 255, 255))
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 25

    def _render_debug_info(self) -> None:
        """Render debug information when debug mode is enabled"""
        font = pygame.font.Font(None, 20)
        y_offset = 100
        
        debug_lines = [
            f"FPS: {self.clock.get_fps():.1f}",
            f"Entities: {len(self.entity_manager.entities)}",
            f"Camera: ({self.camera_x:.1f}, {self.camera_y:.1f})",
            f"Zoom: {self.zoom_level}x"
        ]
        
        for line in debug_lines:
            text_surface = font.render(line, True, (255, 255, 0))
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 20
