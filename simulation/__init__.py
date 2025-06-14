"""
2D Top-Down Life Survival Simulation
A complex simulation featuring autonomous AI-driven characters, emergent behavior,
and a fully simulated world with dynamic ecosystems and social interactions.
"""

import os
import sys
from pathlib import Path

# Add the project root directory to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Ensure required directories exist
REQUIRED_DIRS = [
    'assets',
    'assets/sprites',
    'assets/fonts',
    'assets/sounds',
    'config',
    'data',
    'logs'
]

for directory in REQUIRED_DIRS:
    os.makedirs(Path(__file__).parent / directory, exist_ok=True)

# Version information
__version__ = '0.1.0'
__author__ = 'BLACKBOXAI'
__description__ = 'A complex life simulation with autonomous AI-driven characters'

# Import core components
from simulation.engine.config import Config
from simulation.engine.game import Game
from simulation.engine.world import World
from simulation.engine.entity import Entity, DNA
from simulation.engine.entity_manager import EntityManager
from simulation.engine.resource_manager import ResourceManager
from simulation.engine.job_system import JobSystem
from simulation.engine.ai_system import AISystem
from simulation.engine.time_system import TimeSystem
from simulation.engine.utils import *

# Initialize logging
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(__file__).parent / 'logs/simulation.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info(f"Initializing Life Survival Simulation v{__version__}")

def initialize_simulation():
    """Initialize and return all core simulation components"""
    try:
        config = Config()
        
        # Initialize core systems
        time_system = TimeSystem(config)
        world = World(config)
        resource_manager = ResourceManager(config)
        entity_manager = EntityManager(config)
        job_system = JobSystem(config)
        ai_system = AISystem(config)
        
        # Create game instance
        game = Game(None, config)  # Screen will be set when running
        
        # Set up cross-references between systems
        game.time_system = time_system
        game.world = world
        game.entity_manager = entity_manager
        game.resource_manager = resource_manager
        game.job_system = job_system
        game.ai_system = ai_system
        
        logger.info("Successfully initialized all simulation systems")
        return game
        
    except Exception as e:
        logger.error(f"Failed to initialize simulation: {e}")
        raise

def run_simulation(screen_width=1024, screen_height=768):
    """Initialize and run the simulation"""
    import pygame
    
    try:
        pygame.init()
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Life Survival Simulation")
        
        game = initialize_simulation()
        game.screen = screen
        
        logger.info("Starting simulation main loop")
        game.run()
        
    except Exception as e:
        logger.error(f"Simulation crashed: {e}")
        raise
        
    finally:
        pygame.quit()
        logger.info("Simulation terminated")

if __name__ == "__main__":
    run_simulation()
