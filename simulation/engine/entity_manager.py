from typing import Dict, List, Optional, Set, Tuple
import pygame
import random
import networkx as nx
from .entity import Entity, DNA

class EntityManager:
    """
    Manages all entities in the simulation, including their creation,
    updates, interactions, and relationships.
    """
    def __init__(self, config):
        self.config = config
        self.entities: Dict[int, Entity] = {}
        self.entity_counter = 0
        self.social_network = nx.Graph()
        
        # Simple name generation
        self.name_prefixes = ["Al", "Ber", "Car", "Dor", "El", "Fal", "Gar", "Hel", "Il", "Jor"]
        self.name_suffixes = ["and", "or", "in", "us", "ix", "ar", "en", "on", "el", "ir"]
        
        # Spatial partitioning for efficient entity lookup
        self.spatial_grid: Dict[Tuple[int, int], Set[int]] = {}
        self.grid_size = 10  # Size of each grid cell
        
        # Relationship tracking
        self.families: Dict[int, Set[int]] = {}  # Family ID to member IDs
        self.family_counter = 0
        
    def _generate_name(self) -> str:
        """Generate a random name for an entity"""
        prefix = random.choice(self.name_prefixes)
        suffix = random.choice(self.name_suffixes)
        return prefix + suffix

    def create_entity(self, x: int, y: int, dna: Optional[DNA] = None,
                     parent_ids: Optional[Tuple[int, int]] = None) -> Entity:
        """Create a new entity and add it to the simulation"""
        # Generate name
        name = self._generate_name()
        
        # Create entity
        entity = Entity(self.config, name, x, y, dna)
        entity_id = self.entity_counter
        self.entity_counter += 1
        
        # Set entity ID and add to tracking systems
        entity.id = entity_id
        self.entities[entity_id] = entity
        self.social_network.add_node(entity_id)
        self._add_to_spatial_grid(entity_id, x, y)
        
        # Handle family relationships if parents exist
        if parent_ids:
            self._process_new_child(entity_id, parent_ids)
        
        return entity

    def _process_new_child(self, child_id: int, parent_ids: Tuple[int, int]) -> None:
        """Process family relationships for a new child"""
        parent1_id, parent2_id = parent_ids
        
        # Find or create family
        family_id = None
        for fid, members in self.families.items():
            if parent1_id in members or parent2_id in members:
                family_id = fid
                break
        
        if family_id is None:
            family_id = self.family_counter
            self.family_counter += 1
            self.families[family_id] = {parent1_id, parent2_id}
        
        # Add child to family
        self.families[family_id].add(child_id)
        
        # Create relationship edges
        self.social_network.add_edge(child_id, parent1_id, 
                                   relationship_type="child_parent",
                                   strength=1.0)
        self.social_network.add_edge(child_id, parent2_id,
                                   relationship_type="child_parent",
                                   strength=1.0)

    def update(self, current_time, world, resource_manager) -> None:
        """Update all entities"""
        # Process entity updates
        for entity_id, entity in self.entities.items():
            if entity.alive:
                # Update position in spatial grid if moved
                old_pos = (entity.x, entity.y)
                
                # Update entity
                entity.update(world, current_time)
                
                # Update spatial grid if position changed
                new_pos = (entity.x, entity.y)
                if old_pos != new_pos:
                    self._update_spatial_position(entity_id, old_pos, new_pos)
                
                # Process interactions
                self._process_entity_interactions(entity_id, world, resource_manager, current_time)
        
        # Process births and deaths
        self._process_lifecycle_events()
        
        # Update social networks
        self._update_social_networks()

    def _process_entity_interactions(self, entity_id: int, world, resource_manager, current_time) -> None:
        """Process interactions between entities and with the environment"""
        entity = self.entities[entity_id]
        
        # Get nearby entities
        nearby_entities = self.get_nearby_entities(entity.x, entity.y, radius=5)
        
        for other_id in nearby_entities:
            if other_id != entity_id:
                other = self.entities[other_id]
                
                # Check for potential interactions
                if self._should_interact(entity, other):
                    self._handle_interaction(entity_id, other_id, current_time)

    def _should_interact(self, entity1: Entity, entity2: Entity) -> bool:
        """Determine if two entities should interact"""
        # Base chance on personality compatibility
        compatibility = self._calculate_compatibility(entity1, entity2)
        
        # Modify based on current needs and goals
        need_alignment = self._check_need_alignment(entity1, entity2)
        
        # Random factor
        chance = random.random()
        
        return chance < (compatibility + need_alignment) / 2

    def _calculate_compatibility(self, entity1: Entity, entity2: Entity) -> float:
        """Calculate personality compatibility between two entities"""
        traits = ['extraversion', 'conscientiousness', 'agreeableness', 
                 'neuroticism', 'openness']
        
        compatibility = 0.0
        for trait in traits:
            diff = abs(getattr(entity1.dna, trait) - getattr(entity2.dna, trait))
            compatibility += 1.0 - diff
        
        return compatibility / len(traits)

    def _check_need_alignment(self, entity1: Entity, entity2: Entity) -> float:
        """Check if entities have complementary needs"""
        # Example: One entity needs social interaction while other can provide it
        alignment = 0.0
        
        if entity1.needs['SOCIAL'] < 50 and entity2.needs['SOCIAL'] > 50:
            alignment += 0.5
        elif entity2.needs['SOCIAL'] < 50 and entity1.needs['SOCIAL'] > 50:
            alignment += 0.5
            
        return alignment

    def _handle_interaction(self, entity1_id: int, entity2_id: int, current_time=None) -> None:
        """Handle an interaction between two entities"""
        entity1 = self.entities[entity1_id]
        entity2 = self.entities[entity2_id]
        
        # Update social network
        if not self.social_network.has_edge(entity1_id, entity2_id):
            self.social_network.add_edge(entity1_id, entity2_id,
                                       interactions=0,
                                       relationship_strength=0.0)
        
        # Increment interaction count
        self.social_network[entity1_id][entity2_id]['interactions'] += 1
        
        # Calculate interaction outcome
        outcome = self._calculate_interaction_outcome(entity1, entity2)
        
        # Update relationship strength
        current_strength = self.social_network[entity1_id][entity2_id]['relationship_strength']
        new_strength = max(-1.0, min(1.0, current_strength + outcome))
        self.social_network[entity1_id][entity2_id]['relationship_strength'] = new_strength
        
        # Convert GameTime to minutes
        time_in_minutes = (current_time.day * 24 * 60 +
                         current_time.hour * 60 +
                         current_time.minute)
        
        # Update entity memories
        interaction_description = self._generate_interaction_description(entity1, entity2, outcome)
        entity1.add_memory("social", interaction_description, abs(outcome), timestamp=time_in_minutes)
        entity2.add_memory("social", interaction_description, abs(outcome), timestamp=time_in_minutes)

    def _calculate_interaction_outcome(self, entity1: Entity, entity2: Entity) -> float:
        """Calculate the outcome of an interaction between two entities"""
        # Base outcome on personality compatibility
        base_outcome = self._calculate_compatibility(entity1, entity2)
        
        # Modify based on current moods and needs
        mood_factor = (entity1.needs.get('MORALE', 50) + 
                      entity2.needs.get('MORALE', 50)) / 200
        
        # Random factor for variety
        random_factor = random.gauss(0, 0.1)
        
        return (base_outcome + mood_factor + random_factor) / 3

    def _generate_interaction_description(self, entity1: Entity, entity2: Entity,
                                       outcome: float) -> str:
        """Generate a description of an interaction"""
        if outcome > 0.5:
            return f"Had a very positive interaction with {entity2.name}"
        elif outcome > 0:
            return f"Had a pleasant conversation with {entity2.name}"
        elif outcome > -0.5:
            return f"Had an awkward interaction with {entity2.name}"
        else:
            return f"Had a negative encounter with {entity2.name}"

    def _process_lifecycle_events(self) -> None:
        """Process births, deaths, and aging"""
        # Process deaths
        dead_entities = [eid for eid, e in self.entities.items() 
                        if not e.alive]
        for eid in dead_entities:
            self._handle_death(eid)
        
        # Process potential births
        self._check_for_births()

    def _handle_death(self, entity_id: int) -> None:
        """Handle the death of an entity"""
        entity = self.entities[entity_id]
        
        # Remove from spatial grid
        self._remove_from_spatial_grid(entity_id, entity.x, entity.y)
        
        # Update social network
        for neighbor in list(self.social_network.neighbors(entity_id)):
            other = self.entities[neighbor]
            other.add_memory("death", f"{entity.name} has died", 1.0)
        
        # Remove from family tracking
        for family in self.families.values():
            family.discard(entity_id)
        
        # Clean up empty families
        self.families = {fid: members for fid, members in self.families.items()
                        if members}

    def _check_for_births(self) -> None:
        """Check for potential new births between compatible entities"""
        for edge in self.social_network.edges(data=True):
            entity1_id, entity2_id, data = edge
            
            # Check if entities are compatible for reproduction
            if (data['relationship_strength'] > 0.8 and
                random.random() < 0.01):  # 1% chance per update
                
                entity1 = self.entities[entity1_id]
                entity2 = self.entities[entity2_id]
                
                # Create child DNA
                child_dna = DNA.combine(entity1.dna, entity2.dna)
                
                # Create child near parents
                child_x = entity1.x + random.randint(-1, 1)
                child_y = entity1.y + random.randint(-1, 1)
                
                self.create_entity(child_x, child_y, child_dna, 
                                 (entity1_id, entity2_id))

    def _update_social_networks(self) -> None:
        """Update social network relationships"""
        # Decay unused relationships
        for edge in self.social_network.edges(data=True):
            entity1_id, entity2_id, data = edge
            
            # Decay relationship strength if no recent interactions
            if data['interactions'] == 0:
                data['relationship_strength'] *= 0.99  # 1% decay
            
            # Reset interaction counter
            data['interactions'] = 0

    def get_nearby_entities(self, x: int, y: int, radius: int) -> Set[int]:
        """Get all entities within a certain radius of a position"""
        nearby = set()
        grid_x = x // self.grid_size
        grid_y = y // self.grid_size
        
        # Check surrounding grid cells
        for dx in range(-radius//self.grid_size, radius//self.grid_size + 1):
            for dy in range(-radius//self.grid_size, radius//self.grid_size + 1):
                cell = (grid_x + dx, grid_y + dy)
                if cell in self.spatial_grid:
                    nearby.update(self.spatial_grid[cell])
        
        return nearby

    def _add_to_spatial_grid(self, entity_id: int, x: int, y: int) -> None:
        """Add an entity to the spatial partitioning grid"""
        grid_x = x // self.grid_size
        grid_y = y // self.grid_size
        cell = (grid_x, grid_y)
        
        if cell not in self.spatial_grid:
            self.spatial_grid[cell] = set()
        self.spatial_grid[cell].add(entity_id)

    def _remove_from_spatial_grid(self, entity_id: int, x: int, y: int) -> None:
        """Remove an entity from the spatial partitioning grid"""
        grid_x = x // self.grid_size
        grid_y = y // self.grid_size
        cell = (grid_x, grid_y)
        
        if cell in self.spatial_grid:
            self.spatial_grid[cell].discard(entity_id)
            if not self.spatial_grid[cell]:
                del self.spatial_grid[cell]

    def _update_spatial_position(self, entity_id: int, old_pos: Tuple[int, int],
                               new_pos: Tuple[int, int]) -> None:
        """Update entity position in spatial grid"""
        self._remove_from_spatial_grid(entity_id, old_pos[0], old_pos[1])
        self._add_to_spatial_grid(entity_id, new_pos[0], new_pos[1])

    def render(self, screen: pygame.Surface, visible_area: pygame.Rect,
              zoom_level: float, camera_x: float, camera_y: float) -> None:
        """Render all visible entities"""
        # Calculate visible grid cells
        start_x = int(camera_x) // self.grid_size
        start_y = int(camera_y) // self.grid_size
        end_x = int(camera_x + visible_area.width + 1) // self.grid_size
        end_y = int(camera_y + visible_area.height + 1) // self.grid_size
        
        # Render entities in visible cells
        for grid_x in range(start_x, end_x + 1):
            for grid_y in range(start_y, end_y + 1):
                cell = (grid_x, grid_y)
                if cell in self.spatial_grid:
                    for entity_id in self.spatial_grid[cell]:
                        entity = self.entities[entity_id]
                        entity.render(screen, camera_x, camera_y, zoom_level)

    def get_entity_at_position(self, pos: Tuple[float, float]) -> Optional[Entity]:
        """Get the entity at a specific world position"""
        grid_x = int(pos[0]) // self.grid_size
        grid_y = int(pos[1]) // self.grid_size
        cell = (grid_x, grid_y)
        
        if cell in self.spatial_grid:
            for entity_id in self.spatial_grid[cell]:
                entity = self.entities[entity_id]
                if (abs(entity.x - pos[0]) < 1 and
                    abs(entity.y - pos[1]) < 1):
                    return entity
        
        return None
