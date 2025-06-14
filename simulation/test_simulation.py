import unittest
import pygame
import numpy as np
import random
from engine.config import Config
from engine.game import Game
from engine.world import World
from engine.entity import Entity, DNA
from engine.entity_manager import EntityManager
from engine.resource_manager import ResourceManager, ResourceType
from engine.job_system import JobSystem
from engine.ai_system import AISystem
from engine.time_system import TimeSystem
from dataclasses import dataclass

class TestSimulation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize pygame without audio and create test screen"""
        # Initialize pygame without audio to avoid ALSA warnings
        pygame.display.init()
        pygame.font.init()
        cls.screen = pygame.Surface((800, 600))  # Test surface
        cls.config = Config()

    def setUp(self):
        """Set up test environment before each test"""
        self.game = Game(self.screen, self.config)
        self.world = World(self.config)
        self.entity_manager = EntityManager(self.config)
        self.resource_manager = ResourceManager(self.config)
        self.job_system = JobSystem(self.config)
        self.ai_system = AISystem(self.config)
        self.time_system = TimeSystem(self.config)

    def test_world_generation(self):
        """Test that world generation creates valid terrain"""
        self.assertEqual(self.world.width, self.config.WORLD.WORLD_WIDTH)
        self.assertEqual(self.world.height, self.config.WORLD.WORLD_HEIGHT)
        
        # Check that elevation values are within expected range
        self.assertTrue(np.all(self.world.elevation >= 0))
        self.assertTrue(np.all(self.world.elevation <= 1))
        
        # Check that biomes are assigned
        self.assertTrue(np.any(self.world.biomes != 0))

    def test_entity_creation(self):
        """Test entity creation and DNA inheritance"""
        # Create parent entities with specific positions
        parent1 = self.entity_manager.create_entity(10, 10)
        parent2 = self.entity_manager.create_entity(11, 11)
        
        # Get their IDs
        parent1_id = next(iter(self.entity_manager.entities.keys()))
        parent2_id = list(self.entity_manager.entities.keys())[1]
        
        # Create child with inherited DNA
        child = self.entity_manager.create_entity(
            12, 12, 
            parent_ids=(parent1_id, parent2_id)
        )
        
        # Verify entity creation
        self.assertIsNotNone(parent1)
        self.assertIsNotNone(parent2)
        self.assertIsNotNone(child)
        
        # Verify DNA inheritance
        self.assertIsNotNone(child.dna)
        self.assertTrue(0 <= child.dna.height <= 1.5)
        self.assertTrue(0 <= child.dna.physical_aptitude <= 1)

    def test_resource_management(self):
        """Test resource spawning and collection"""
        # Add a test resource directly
        test_pos = (5, 5)
        self.resource_manager.add_resource(
            test_pos,
            ResourceType.TREE,
            quantity=100.0,
            quality=0.8
        )
        
        # Check that resource was added
        self.assertIn(test_pos, self.resource_manager.resources)
        
        # Test resource collection
        result = self.resource_manager.collect_resource(test_pos, 10)
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], ResourceType.TREE)
        self.assertTrue(0 <= result[1] <= 10)  # Collected amount
        self.assertEqual(result[2], 0.8)       # Quality

    def test_time_system(self):
        """Test time progression and calendar system"""
        initial_time = self.time_system.current_time.copy()
        
        # Progress time
        for _ in range(100):
            self.time_system.update()
        
        # Verify time progression
        current_time = self.time_system.current_time
        self.assertGreater(
            current_time.minute + 
            current_time.hour * 60 + 
            current_time.day * 24 * 60,
            initial_time.minute +
            initial_time.hour * 60 +
            initial_time.day * 24 * 60
        )
        
        # Test calendar features
        weekday = self.time_system.get_weekday()
        self.assertIsNotNone(weekday)
        
        time_of_day = self.time_system.get_time_of_day()
        self.assertIsNotNone(time_of_day)

    def test_job_system(self):
        """Test job assignment and work processing"""
        # Create a test entity
        entity = self.entity_manager.create_entity(5, 5)
        
        # Get available jobs
        available_jobs = self.job_system.get_available_jobs(entity.id)
        self.assertIsInstance(available_jobs, list)
        
        # Try to assign a job
        if available_jobs:
            success = self.job_system.assign_job(entity.id, available_jobs[0])
            self.assertTrue(success)
            self.assertIn(entity.id, self.job_system.active_workers)

    def test_ai_system(self):
        """Test AI behavior and decision making"""
        # Create test entity
        entity = self.entity_manager.create_entity(7, 7)
        
        # Add some test memories with timestamp
        current_time = self.time_system.current_time.minute + \
                      self.time_system.current_time.hour * 60 + \
                      self.time_system.current_time.day * 24 * 60
        
        self.ai_system.add_memory(
            entity.id,
            "test",
            "Test memory",
            1.0,
            [entity.id],  # Include the entity ID in the entities list
            (7, 7),
            ["test"],
            timestamp=current_time
        )
        
        # Verify memory storage
        memories = self.ai_system.get_memories_about(entity.id, entity.id)
        self.assertGreater(len(memories), 0)
        
        # Test AI update
        self.ai_system.update(entity.id, entity, self.world, 
                            self.time_system.current_time)
        
        # Verify goal generation
        self.assertIn(entity.id, self.ai_system.entity_goals)
        self.assertIsInstance(self.ai_system.entity_goals[entity.id], list)

    def test_game_integration(self):
        """Test that all systems work together"""
        # Set up game with all systems
        self.game.time_system = self.time_system
        self.game.world = self.world
        self.game.entity_manager = self.entity_manager
        self.game.resource_manager = self.resource_manager
        self.game.job_system = self.job_system
        self.game.ai_system = self.ai_system
        
        # Create some test entities
        for _ in range(5):
            self.entity_manager.create_entity(
                random.randint(0, self.world.width-1),
                random.randint(0, self.world.height-1)
            )
        
        # Add some test resources
        self.resource_manager.add_resource(
            (5, 5),
            ResourceType.TREE,
            quantity=100.0,
            quality=0.8
        )
        
        # Run a few game updates
        for _ in range(10):
            self.game.update()
            
        # Verify game state
        self.assertTrue(len(self.entity_manager.entities) > 0)
        self.assertTrue(len(self.resource_manager.resources) > 0)
        self.assertFalse(self.game.paused)

    def tearDown(self):
        """Clean up after each test"""
        pass

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests"""
        pygame.quit()

if __name__ == '__main__':
    unittest.main()
