from typing import Dict, List, Optional, Set, Tuple
import random
from dataclasses import dataclass
from enum import Enum, auto

class ResourceType(Enum):
    """Types of resources available in the world"""
    # Basic Resources
    TREE = "TREE"
    BUSH = "BUSH"
    HERB = "HERB"
    STONE = "STONE"
    METAL = "METAL"
    GEMSTONE = "GEMSTONE"
    VEGETABLE = "VEGETABLE"
    MINERAL = "MINERAL"
    FISH = "FISH"
    SHELL = "SHELL"
    CORAL = "CORAL"
    
    # Advanced Resources (Crafted/Processed)
    LUMBER = "LUMBER"
    CLOTH = "CLOTH"
    METAL_INGOT = "METAL_INGOT"
    GEMSTONE_CUT = "GEMSTONE_CUT"
    HERB_DRIED = "HERB_DRIED"
    FOOD_COOKED = "FOOD_COOKED"
    POTION = "POTION"
    TOOL = "TOOL"
    WEAPON = "WEAPON"
    ARMOR = "ARMOR"

@dataclass
class Resource:
    """Represents a resource instance in the world"""
    type: ResourceType
    quantity: float
    quality: float
    position: Tuple[int, int]
    regeneration_rate: float
    max_quantity: float
    last_update: int  # Timestamp of last update

@dataclass
class Recipe:
    """Defines a crafting recipe"""
    name: str
    ingredients: Dict[ResourceType, int]
    tools_required: List[str]
    skills_required: Dict[str, int]
    time_required: int
    difficulty: float
    product_type: str
    product_quantity: int
    quality_factors: Dict[str, float]

class ResourceManager:
    """
    Manages all resources in the simulation, including:
    - Resource spawning and regeneration
    - Resource collection and depletion
    - Crafting system
    - Resource distribution across biomes
    """
    def __init__(self, config):
        self.config = config
        self.resources: Dict[Tuple[int, int], Resource] = {}
        self.recipes: Dict[str, Recipe] = self._initialize_recipes()
        
        # Resource distribution rules
        self.biome_resources = {
            "BOREAL_FOREST": {
                ResourceType.TREE: 0.4,
                ResourceType.BUSH: 0.2,
                ResourceType.HERB: 0.1,
                ResourceType.STONE: 0.1
            },
            "DECIDUOUS_FOREST": {
                ResourceType.TREE: 0.5,
                ResourceType.BUSH: 0.3,
                ResourceType.VEGETABLE: 0.2,
                ResourceType.HERB: 0.2
            },
            "MOUNTAIN": {
                ResourceType.STONE: 0.5,
                ResourceType.METAL: 0.3,
                ResourceType.GEMSTONE: 0.1
            },
            "PLAINS": {
                ResourceType.HERB: 0.4,
                ResourceType.BUSH: 0.3,
                ResourceType.VEGETABLE: 0.3
            },
            "COASTAL": {
                ResourceType.FISH: 0.4,
                ResourceType.SHELL: 0.3,
                ResourceType.CORAL: 0.2
            }
        }

    def _initialize_recipes(self) -> Dict[str, Recipe]:
        """Initialize all crafting recipes"""
        recipes = {}
        
        # Basic Tools
        recipes["wooden_axe"] = Recipe(
            name="Wooden Axe",
            ingredients={ResourceType.TREE: 2},
            tools_required=[],
            skills_required={"Carpentry": 10},
            time_required=30,
            difficulty=0.3,
            product_type="tool",
            product_quantity=1,
            quality_factors={"Carpentry": 0.7, "Wood Quality": 0.3}
        )
        
        recipes["stone_pickaxe"] = Recipe(
            name="Stone Pickaxe",
            ingredients={ResourceType.STONE: 3, ResourceType.TREE: 2},
            tools_required=["axe"],
            skills_required={"Carpentry": 15, "Smithing": 10},
            time_required=45,
            difficulty=0.4,
            product_type="tool",
            product_quantity=1,
            quality_factors={"Smithing": 0.6, "Stone Quality": 0.4}
        )
        
        # Add more recipes...
        
        return recipes

    def spawn_resources(self, world) -> None:
        """Spawn initial resources based on biome types"""
        for y in range(world.height):
            for x in range(world.width):
                biome = world.get_biome_at(x, y)
                if biome in self.biome_resources:
                    self._spawn_biome_resources(x, y, biome)

    def _spawn_biome_resources(self, x: int, y: int, biome: str) -> None:
        """Spawn resources for a specific biome tile"""
        for resource_type, probability in self.biome_resources[biome].items():
            if random.random() < probability:
                resource = Resource(
                    type=resource_type,
                    quantity=random.uniform(0.5, 1.0) * 100,
                    quality=random.uniform(0.3, 1.0),
                    position=(x, y),
                    regeneration_rate=0.01,  # 1% per update
                    max_quantity=100,
                    last_update=0
                )
                self.resources[(x, y)] = resource

    def update(self, current_time, world) -> None:
        """Update resource states"""
        # Update resource regeneration
        for resource in self.resources.values():
            if resource.quantity < resource.max_quantity:
                time_diff = current_time - resource.last_update
                regen_amount = resource.regeneration_rate * time_diff
                resource.quantity = min(
                    resource.max_quantity,
                    resource.quantity + regen_amount
                )
            resource.last_update = current_time

    def collect_resource(self, position: Tuple[int, int], 
                        amount: float, tool_quality: float = 1.0) -> Optional[Tuple[ResourceType, float, float]]:
        """
        Attempt to collect a resource from a position
        Returns (resource_type, quantity, quality) if successful
        """
        if position not in self.resources:
            return None
            
        resource = self.resources[position]
        if resource.quantity < amount:
            return None
            
        # Apply tool quality bonus
        collected_amount = min(amount * tool_quality, resource.quantity)
        resource.quantity -= collected_amount
        
        # Remove resource if depleted
        if resource.quantity <= 0:
            del self.resources[position]
            
        return (resource.type, collected_amount, resource.quality)

    def can_craft(self, recipe_name: str, inventory: Dict[ResourceType, float],
                  tools: List[str], skills: Dict[str, int]) -> bool:
        """Check if a recipe can be crafted with given resources and skills"""
        if recipe_name not in self.recipes:
            return False
            
        recipe = self.recipes[recipe_name]
        
        # Check ingredients
        for ingredient, amount in recipe.ingredients.items():
            if ingredient not in inventory or inventory[ingredient] < amount:
                return False
                
        # Check tools
        for tool in recipe.tools_required:
            if tool not in tools:
                return False
                
        # Check skills
        for skill, level in recipe.skills_required.items():
            if skill not in skills or skills[skill] < level:
                return False
                
        return True

    def craft_item(self, recipe_name: str, inventory: Dict[ResourceType, float],
                   tools: List[str], skills: Dict[str, int]) -> Optional[Tuple[str, int, float]]:
        """
        Attempt to craft an item
        Returns (product_type, quantity, quality) if successful
        """
        if not self.can_craft(recipe_name, inventory, tools, skills):
            return None
            
        recipe = self.recipes[recipe_name]
        
        # Consume ingredients
        for ingredient, amount in recipe.ingredients.items():
            inventory[ingredient] -= amount
            
        # Calculate quality based on skills and ingredients
        quality = self._calculate_craft_quality(recipe, skills)
        
        return (recipe.product_type, recipe.product_quantity, quality)

    def _calculate_craft_quality(self, recipe: Recipe, skills: Dict[str, int]) -> float:
        """Calculate the quality of a crafted item based on skills and factors"""
        quality = 0.0
        total_weight = 0.0
        
        for factor, weight in recipe.quality_factors.items():
            if factor in skills:
                quality += skills[factor] * weight
            total_weight += weight
            
        return quality / total_weight if total_weight > 0 else 0.5

    def get_nearby_resources(self, x: int, y: int, radius: int) -> List[Tuple[Tuple[int, int], Resource]]:
        """Get all resources within a certain radius"""
        nearby = []
        for pos, resource in self.resources.items():
            dx = abs(pos[0] - x)
            dy = abs(pos[1] - y)
            if dx <= radius and dy <= radius:
                nearby.append((pos, resource))
        return nearby

    def get_resource_at(self, position: Tuple[int, int]) -> Optional[Resource]:
        """Get the resource at a specific position"""
        return self.resources.get(position)

    def add_resource(self, position: Tuple[int, int], resource_type: ResourceType,
                    quantity: float, quality: float) -> None:
        """Add a new resource to the world"""
        if position not in self.resources:
            self.resources[position] = Resource(
                type=resource_type,
                quantity=quantity,
                quality=quality,
                position=position,
                regeneration_rate=0.01,
                max_quantity=quantity,
                last_update=0
            )

    def remove_resource(self, position: Tuple[int, int]) -> None:
        """Remove a resource from the world"""
        if position in self.resources:
            del self.resources[position]
