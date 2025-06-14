
from typing import Dict, List, Optional, Set, Tuple
import random
import networkx as nx
from dataclasses import dataclass, field
from enum import Enum, auto

class BehaviorType(Enum):
    """Types of behaviors an entity can exhibit"""
    SURVIVAL = auto()    # Basic needs like eating, drinking, sleeping
    SOCIAL = auto()      # Interactions with other entities
    WORK = auto()        # Job-related activities
    LEISURE = auto()     # Entertainment and relaxation
    COMBAT = auto()      # Fighting and defense
    EXPLORE = auto()     # World exploration
    LEARN = auto()       # Skill improvement
    CREATE = auto()      # Building and crafting
    TRADE = auto()       # Economic activities

@dataclass
class Memory:
    """Detailed memory of an event or interaction"""
    timestamp: int
    type: str
    description: str
    entities_involved: List[int]
    location: Tuple[int, int]
    emotional_impact: float
    importance: float
    tags: List[str]

@dataclass
class Goal:
    """Represents a specific goal an entity wants to achieve"""
    type: str
    priority: float
    target: Optional[object]
    requirements: Dict[str, float]
    deadline: Optional[int]
    progress: float = 0.0
    subtasks: List['Task'] = field(default_factory=list)

@dataclass
class Task:
    """A specific task to accomplish a goal"""
    type: str
    priority: float
    duration: int
    progress: float = 0.0
    requirements: Dict[str, float] = field(default_factory=dict)
    location: Optional[Tuple[int, int]] = None

class AISystem:
    """
    Manages AI behavior, decision making, and social interactions.
    Features:
    - Memory and personality-based decision making
    - Dynamic goal generation and planning
    - Social relationship management
    - Learning and skill development
    - Emotional state tracking
    """
    def __init__(self, config):
        self.config = config
        self.entity_goals: Dict[int, List[Goal]] = {}
        self.entity_memories: Dict[int, List[Memory]] = {}
        self.social_networks: Dict[int, nx.Graph] = {}
        self.current_tasks: Dict[int, Task] = {}
        
        # Behavior weights for different personality types
        self.personality_behaviors = {
            "extravert": {
                BehaviorType.SOCIAL: 0.8,
                BehaviorType.LEISURE: 0.6,
                BehaviorType.WORK: 0.4
            },
            "introvert": {
                BehaviorType.SOCIAL: 0.3,
                BehaviorType.LEARN: 0.7,
                BehaviorType.CREATE: 0.6
            },
            # Add more personality types...
        }

    def update(self, entity_id: int, entity, world, current_time) -> None:
        """Update AI state for an entity"""
        # Update needs and emotional state
        self._update_emotional_state(entity)
        
        # Process memories and forget old ones
        self._process_memories(entity_id, current_time)
        
        # Update goals
        self._update_goals(entity_id, entity, current_time)
        
        # Make decisions and take actions
        self._make_decisions(entity_id, entity, world, current_time)

    def _update_emotional_state(self, entity) -> None:
        """Update entity's emotional state based on needs and events"""
        # Base mood affected by needs
        base_mood = sum(
            need_value * self.config.NEEDS_CONFIG[need_name]["priority"]
            for need_name, need_value in entity.needs.items()
        ) / sum(config["priority"] for config in self.config.NEEDS_CONFIG.values())
        
        # Personality influence
        personality_modifier = (
            entity.dna.extraversion * 0.3 +
            entity.dna.neuroticism * -0.3 +
            entity.dna.agreeableness * 0.2
        )
        
        # Recent memory influence
        memory_impact = self._calculate_memory_impact(entity.id)
        
        # Set final emotional state
        entity.emotional_state = base_mood + personality_modifier + memory_impact

    def _process_memories(self, entity_id: int, current_time) -> None:
        """Process and manage entity memories"""
        if entity_id not in self.entity_memories:
            self.entity_memories[entity_id] = []
            
        memories = self.entity_memories[entity_id]
        
        # Convert GameTime to minutes for comparison
        current_minutes = (current_time.day * 24 * 60 + 
                         current_time.hour * 60 + 
                         current_time.minute)
        
        # Forget old memories based on importance
        memories = [
            mem for mem in memories
            if (current_minutes - mem.timestamp < 10000) or  # Keep recent memories
               (random.random() < mem.importance)            # Keep important ones
        ]
        # Consolidate similar memories
        self._consolidate_memories(memories)
        
        self.entity_memories[entity_id] = memories

    def _consolidate_memories(self, memories: List[Memory]) -> None:
        """Combine similar memories to form more general ones"""
        i = 0
        while i < len(memories) - 1:
            j = i + 1
            while j < len(memories):
                if self._are_memories_similar(memories[i], memories[j]):
                    # Combine memories
                    memories[i].importance += memories[j].importance * 0.5
                    memories[i].description = f"Repeatedly {memories[i].description}"
                    memories.pop(j)
                else:
                    j += 1
            i += 1

    def _are_memories_similar(self, mem1: Memory, mem2: Memory) -> bool:
        """Check if two memories are similar enough to consolidate"""
        return (
            mem1.type == mem2.type and
            set(mem1.tags) & set(mem2.tags) and  # Common tags
            abs(mem1.emotional_impact - mem2.emotional_impact) < 0.3
        )

    def _calculate_memory_impact(self, entity_id: int) -> float:
        """Calculate emotional impact of recent memories"""
        if entity_id not in self.entity_memories:
            return 0.0
            
        recent_memories = sorted(
            self.entity_memories[entity_id],
            key=lambda m: m.timestamp,
            reverse=True
        )[:10]  # Consider last 10 memories
        
        total_impact = sum(mem.emotional_impact * mem.importance 
                          for mem in recent_memories)
        return total_impact / len(recent_memories) if recent_memories else 0.0

    def _update_goals(self, entity_id: int, entity, current_time: int) -> None:
        """Update and reprioritize entity goals"""
        if entity_id not in self.entity_goals:
            self.entity_goals[entity_id] = []
            
        goals = self.entity_goals[entity_id]
        
        # Remove completed or impossible goals
        goals = [goal for goal in goals if not self._is_goal_complete(goal)
                and not self._is_goal_impossible(goal, entity)]
        
        # Generate new goals based on needs and personality
        new_goals = self._generate_goals(entity)
        goals.extend(new_goals)
        
        # Prioritize goals
        goals.sort(key=lambda g: self._calculate_goal_priority(g, entity), 
                  reverse=True)
        
        self.entity_goals[entity_id] = goals[:5]  # Keep top 5 goals

    def _generate_goals(self, entity) -> List[Goal]:
        """Generate new goals based on entity state"""
        new_goals = []
        
        # Check urgent needs
        for need_name, value in entity.needs.items():
            if value < 30:  # Below 30% is urgent
                new_goals.append(Goal(
                    type="satisfy_need",
                    priority=1.0 - (value / 100),
                    target=need_name,
                    requirements={},
                    deadline=None
                ))
        
        # Career goals based on skills
        if random.random() < 0.1:  # 10% chance each update
            best_skill = max(entity.skills.items(), key=lambda x: x[1])[0]
            new_goals.append(Goal(
                type="improve_skill",
                priority=0.5,
                target=best_skill,
                requirements={best_skill: entity.skills[best_skill] + 10},
                deadline=None
            ))
        
        # Social goals based on personality
        if entity.dna.extraversion > 0.6 and entity.needs.get("SOCIAL", 100) < 70:
            new_goals.append(Goal(
                type="socialize",
                priority=0.6,
                target=None,
                requirements={},
                deadline=None
            ))
        
        return new_goals

    def _calculate_goal_priority(self, goal: Goal, entity) -> float:
        """Calculate current priority of a goal"""
        base_priority = goal.priority
        
        # Modify based on needs
        if goal.type == "satisfy_need":
            need_value = entity.needs.get(goal.target, 100)
            base_priority *= (1.0 - (need_value / 100))
        
        # Modify based on deadline
        if goal.deadline:
            time_left = goal.deadline - self.config.time_system.current_time
            if time_left > 0:
                base_priority *= 1 + (1 / time_left)
        
        # Personality influence
        if goal.type == "socialize":
            base_priority *= entity.dna.extraversion
        elif goal.type == "improve_skill":
            base_priority *= entity.dna.conscientiousness
        
        return base_priority

    def _make_decisions(self, entity_id: int, entity, world, current_time) -> None:
        """Make decisions and take actions based on goals and state"""
        # Check if current task should continue
        current_task = self.current_tasks.get(entity_id)
        if current_task and not self._should_abandon_task(current_task, entity):
            self._continue_task(entity_id, entity, current_task, world)
            return
            
        # Get highest priority goal
        goals = self.entity_goals.get(entity_id, [])
        if not goals:
            return  # Just do nothing when no goals exist
            
        goal = goals[0]
        
        # Plan new task for goal
        new_task = self._plan_task(goal, entity, world)
        if new_task:
            self.current_tasks[entity_id] = new_task
            self._start_task(entity_id, entity, new_task, world)

    def _should_abandon_task(self, task: Task, entity) -> bool:
        """Determine if current task should be abandoned"""
        # Check if urgent needs should interrupt
        for need_name, value in entity.needs.items():
            if value < 20 and self.config.NEEDS_CONFIG[need_name]["priority"] < 3:
                return True
                
        # Check if task is still possible
        for req_name, req_value in task.requirements.items():
            if req_name in entity.stats and entity.stats[req_name] < req_value:
                return True
                
        return False

    def _plan_task(self, goal: Goal, entity, world) -> Optional[Task]:
        """Plan a specific task to achieve a goal"""
        if goal.type == "satisfy_need":
            return self._plan_need_satisfaction(goal.target, entity, world)
        elif goal.type == "improve_skill":
            return self._plan_skill_improvement(goal.target, entity)
        elif goal.type == "socialize":
            return self._plan_social_interaction(entity, world)
        # Add more goal type handlers...
        
        return None

    def _plan_need_satisfaction(self, need: str, entity, world) -> Optional[Task]:
        """Plan a task to satisfy a specific need"""
        if need == "HUNGER":
            # Find food source
            food_location = self._find_nearest_resource(entity, "FOOD", world)
            if food_location:
                return Task(
                    type="get_food",
                    priority=0.8,
                    duration=20,
                    location=food_location
                )
        elif need == "THIRST":
            # Find water source
            water_location = self._find_nearest_resource(entity, "WATER", world)
            if water_location:
                return Task(
                    type="get_water",
                    priority=0.9,
                    duration=10,
                    location=water_location
                )
        # Add more need handlers...
        
        return None

    def _find_nearest_resource(self, entity, resource_type: str, 
                             world) -> Optional[Tuple[int, int]]:
        """Find nearest resource of given type"""
        # This would need to interface with the resource manager
        # Implementation depends on how resources are stored
        pass

    def add_memory(self, entity_id: int, memory_type: str, description: str,
                  importance: float, entities: List[int] = None,
                  location: Optional[Tuple[int, int]] = None,
                  tags: List[str] = None, timestamp: Optional[int] = None) -> None:
        """Add a new memory to an entity"""
        if entity_id not in self.entity_memories:
            self.entity_memories[entity_id] = []
            
        memory = Memory(
            timestamp=timestamp or 0,  # Use provided timestamp or default to 0
            type=memory_type,
            description=description,
            entities_involved=entities or [],
            location=location,
            emotional_impact=random.uniform(-1.0, 1.0),  # Could be more sophisticated
            importance=importance,
            tags=tags or []
        )
        
        self.entity_memories[entity_id].append(memory)

    def get_memories_about(self, entity_id: int, 
                         target_id: int) -> List[Memory]:
        """Get all memories involving a specific entity"""
        if entity_id not in self.entity_memories:
            return []
            
        return [mem for mem in self.entity_memories[entity_id]
                if target_id in mem.entities_involved]

    def get_emotional_state(self, entity_id: int) -> Dict[str, float]:
        """Get current emotional state metrics"""
        # This would need to be implemented based on how emotional state is tracked
        pass
