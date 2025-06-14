import random
from typing import Dict, List, Optional, Tuple
import pygame
import networkx as nx
from dataclasses import dataclass, field
import numpy as np

@dataclass
class DNA:
    """Genetic information that determines entity traits and appearance"""
    # Physical traits
    height: float = 1.0  # Normalized height (0.5 to 1.5)
    build: float = 1.0   # Body build (0.5 to 1.5)
    skin_tone: Tuple[int, int, int] = (255, 220, 177)  # RGB
    hair_color: Tuple[int, int, int] = (101, 67, 33)   # RGB
    
    # Personality base traits (0-1 scale)
    extraversion: float = 0.5
    conscientiousness: float = 0.5
    agreeableness: float = 0.5
    neuroticism: float = 0.5
    openness: float = 0.5
    
    # Skill aptitudes (0-1 scale)
    physical_aptitude: float = 0.5
    mental_aptitude: float = 0.5
    social_aptitude: float = 0.5
    crafting_aptitude: float = 0.5
    magical_aptitude: float = 0.5

    @classmethod
    def combine(cls, dna1: 'DNA', dna2: 'DNA') -> 'DNA':
        """Create a new DNA by combining two parent DNAs with mutation"""
        def mix(v1, v2, mutation_rate=0.1):
            base = (v1 + v2) / 2
            mutation = random.gauss(0, mutation_rate)
            return max(0, min(1, base + mutation))

        def mix_color(c1, c2):
            return tuple(int((a + b) / 2) for a, b in zip(c1, c2))

        return cls(
            height=mix(dna1.height, dna2.height),
            build=mix(dna1.build, dna2.build),
            skin_tone=mix_color(dna1.skin_tone, dna2.skin_tone),
            hair_color=mix_color(dna1.hair_color, dna2.hair_color),
            extraversion=mix(dna1.extraversion, dna2.extraversion),
            conscientiousness=mix(dna1.conscientiousness, dna2.conscientiousness),
            agreeableness=mix(dna1.agreeableness, dna2.agreeableness),
            neuroticism=mix(dna1.neuroticism, dna2.neuroticism),
            openness=mix(dna1.openness, dna2.openness),
            physical_aptitude=mix(dna1.physical_aptitude, dna2.physical_aptitude),
            mental_aptitude=mix(dna1.mental_aptitude, dna2.mental_aptitude),
            social_aptitude=mix(dna1.social_aptitude, dna2.social_aptitude),
            crafting_aptitude=mix(dna1.crafting_aptitude, dna2.crafting_aptitude),
            magical_aptitude=mix(dna1.magical_aptitude, dna2.magical_aptitude)
        )

@dataclass
class Memory:
    """Represents a single memory of an event or interaction"""
    timestamp: int
    type: str
    description: str
    importance: float
    entities_involved: List[int] = field(default_factory=list)
    location: Optional[Tuple[int, int]] = None
    emotional_impact: float = 0.0

class Entity:
    """
    Base class for all entities in the simulation (characters, creatures, etc.)
    Handles DNA, stats, skills, needs, memories, and relationships
    """
    def __init__(self, config, name: str, x: int, y: int, dna: Optional[DNA] = None):
        self.config = config
        self.name = name
        self.x = x
        self.y = y
        self.dna = dna or DNA()
        self.id = None  # Will be set by EntityManager
        
        # Initialize core systems
        self.needs = self._initialize_needs()
        self.stats = self._initialize_stats()
        self.skills = self._initialize_skills()
        self.memories = []
        self.relationships = nx.Graph()
        
        # State tracking
        self.current_task = None
        self.inventory = []
        self.age = 0
        self.alive = True
        self.health = 100
        
        # Action and behavior
        self.action_queue = []
        self.current_action = None
        self.daily_schedule = {}
        
        # Appearance
        self.sprite = self._generate_sprite()

    def _initialize_needs(self) -> Dict[str, float]:
        """Initialize needs with values from config"""
        return {
            need: self.config.NEEDS_CONFIG[need]["max"]
            for need in self.config.NEEDS_CONFIG.keys()
        }

    def _initialize_stats(self) -> Dict[str, float]:
        """Initialize stats based on DNA"""
        return {
            "Strength": 50 + self.dna.physical_aptitude * 50,
            "Dexterity": 50 + self.dna.physical_aptitude * 50,
            "Intelligence": 50 + self.dna.mental_aptitude * 50,
            "Wisdom": 50 + self.dna.mental_aptitude * 50,
            "Charisma": 50 + self.dna.social_aptitude * 50,
            "Constitution": 50 + self.dna.physical_aptitude * 50
        }

    def _initialize_skills(self) -> Dict[str, float]:
        """Initialize skills with base values"""
        return {skill: 0 for skill in self.config.SKILL_CONFIG}

    def _generate_sprite(self) -> pygame.Surface:
        """Generate a procedural pixel sprite based on DNA traits"""
        from .sprite_generator import SpriteGenerator
        
        # Create sprite generator with size based on DNA height
        size = int(16 * self.dna.height)  # Base size modified by height
        generator = SpriteGenerator(size)
        
        # Use entity ID as seed for consistent generation
        seed = hash(str(self.dna.height) + str(self.dna.skin_tone) + str(self.dna.hair_color))
        
        # Generate base sprite
        sprite = generator.generate_sprite(seed)
        
        # Generate animation frames
        self.animation_frames = generator.generate_animation_frames(sprite)
        self.current_frame = 0
        
        return sprite

    def update(self, world, time_system) -> None:
        """Update entity state for the current tick"""
        if not self.alive:
            return
            
        # Update needs
        self._update_needs()
        
        # Process current action or get new one
        if not self.current_action:
            self._decide_next_action(world, time_system)
        else:
            self._process_current_action(world)
        
        # Age and check for death conditions
        self._check_survival()

    def _update_needs(self) -> None:
        """Update all needs based on decay rates"""
        for need, value in self.needs.items():
            decay = self.config.NEEDS_CONFIG[need]["decay"]
            min_val = self.config.NEEDS_CONFIG[need]["min"]
            max_val = self.config.NEEDS_CONFIG[need]["max"]
            
            self.needs[need] = max(min_val, min(max_val, value - decay))

    def _decide_next_action(self, world, time_system) -> None:
        """Decide the next action based on needs, schedule, and environment"""
        # Check schedule first
        current_hour = time_system.hour
        if current_hour in self.daily_schedule:
            self.current_action = self.daily_schedule[current_hour]
            return
            
        # Otherwise, check needs and environment
        urgent_needs = self._get_urgent_needs()
        if urgent_needs:
            self.current_action = self._plan_action_for_need(urgent_needs[0], world)
        else:
            self.current_action = self._get_default_action()

    def _process_current_action(self, world) -> None:
        """Process the current action"""
        # For now, just clear the current action
        self.current_action = None

    def _get_urgent_needs(self) -> List[str]:
        """Get list of needs below threshold, sorted by priority"""
        urgent = []
        for need, value in self.needs.items():
            config = self.config.NEEDS_CONFIG[need]
            threshold = config["max"] * 0.3  # 30% of max is urgent
            if value < threshold:
                urgent.append((need, config["priority"]))
        
        return [need for need, _ in sorted(urgent, key=lambda x: x[1])]

    def _get_default_action(self) -> str:
        """Get a default action when no urgent needs exist"""
        return "IDLE"

    def add_memory(self, memory_type: str, description: str, 
                  importance: float, entities: List[int] = None,
                  location: Tuple[int, int] = None, timestamp: Optional[int] = None) -> None:
        """Add a new memory"""
        memory = Memory(
            timestamp=timestamp or 0,  # Use provided timestamp or default to 0
            type=memory_type,
            description=description,
            importance=importance,
            entities_involved=entities or [],
            location=location or (self.x, self.y)
        )
        self.memories.append(memory)
        
        # Limit memory size and forget least important memories
        if len(self.memories) > 1000:  # Arbitrary limit
            self.memories.sort(key=lambda m: m.importance)
            self.memories = self.memories[-1000:]

    def modify_relationship(self, other_entity: 'Entity', 
                          change: float, reason: str) -> None:
        """Modify relationship with another entity"""
        if other_entity not in self.relationships:
            self.relationships.add_node(other_entity, 
                                     relationship=0.0, 
                                     interactions=[])
        
        current = self.relationships.nodes[other_entity]["relationship"]
        new_value = max(-1.0, min(1.0, current + change))
        self.relationships.nodes[other_entity]["relationship"] = new_value
        
        # Record interaction
        self.relationships.nodes[other_entity]["interactions"].append({
            "time": self.config.time_system.current_time,
            "change": change,
            "reason": reason
        })

    def render(self, screen: pygame.Surface, camera_x: int, 
              camera_y: int, zoom: float) -> None:
        """Render the entity on the screen with animation"""
        if not self.alive:
            return
            
        # Calculate screen position
        screen_x = int((self.x - camera_x) * self.config.WORLD.TILE_SIZE * zoom)
        screen_y = int((self.y - camera_y) * self.config.WORLD.TILE_SIZE * zoom)
        
        # Get current animation frame
        current_sprite = self.animation_frames[self.current_frame]
        
        # Update animation frame (cycle through frames)
        self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
        
        # Scale sprite based on zoom
        scaled_size = int(current_sprite.get_width() * zoom)
        scaled_sprite = pygame.transform.scale(
            current_sprite, (scaled_size, scaled_size))
        
        # Draw sprite
        screen.blit(scaled_sprite, (screen_x, screen_y))

    def _check_survival(self) -> None:
        """Check if entity should die based on health and needs"""
        if self.health <= 0:
            self.alive = False
            return
            
        # Check critical needs
        for need, value in self.needs.items():
            if need in ["HEALTH", "THIRST", "HUNGER"]:
                if value <= 0:
                    self.alive = False
                    return

    def get_memory_summary(self) -> str:
        """Get a summary of important memories"""
        important_memories = sorted(
            [m for m in self.memories if m.importance > 0.7],
            key=lambda m: m.importance,
            reverse=True
        )
        
        summary = []
        for memory in important_memories[:5]:  # Top 5 memories
            summary.append(f"{memory.type}: {memory.description}")
        
        return "\n".join(summary)
