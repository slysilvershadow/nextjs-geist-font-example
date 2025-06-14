from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field

class JobCategory(Enum):
    """Main categories of jobs"""
    CONSTRUCTION = "Construction & Infrastructure"
    FARMING = "Farming & Resource Gathering"
    CRAFTING = "Crafting & Production"
    FOOD = "Food & Drink"
    DEFENSE = "Defense & Warfare"
    TRADE = "Trade & Communication"
    MEDICINE = "Medicine & Magic"
    ARTS = "Arts & Culture"
    EXPLORATION = "Exploration & Defense"

@dataclass
class JobRequirement:
    """Requirements for a job"""
    min_skills: Dict[str, int]
    required_tools: List[str]
    workspace_type: Optional[str]
    min_stats: Dict[str, int]

@dataclass
class JobProduct:
    """Output of a job"""
    resource_type: str
    base_quantity: float
    quality_factors: Dict[str, float]

@dataclass
class Job:
    """Defines a specific job type"""
    name: str
    category: JobCategory
    description: str
    requirements: JobRequirement
    products: List[JobProduct]
    base_wage: float
    skill_experience: Dict[str, float]
    work_hours: Tuple[int, int]  # Start and end hour
    stress_factor: float
    social_factor: float
    danger_level: float

class JobSystem:
    """
    Manages all job-related functionality including:
    - Job definitions and requirements
    - Work scheduling and assignments
    - Skill development and career progression
    - Economic impact and wages
    """
    def __init__(self, config):
        self.config = config
        self.jobs: Dict[str, Job] = self._initialize_jobs()
        self.active_workers: Dict[int, str] = {}  # Entity ID to job name
        self.workplaces: Dict[str, List[Tuple[int, int]]] = {}  # Job name to locations
        
    def _initialize_jobs(self) -> Dict[str, Job]:
        """Initialize all job definitions"""
        jobs = {}
        
        # Construction & Infrastructure Jobs
        jobs["architect"] = Job(
            name="Architect",
            category=JobCategory.CONSTRUCTION,
            description="Plans and surveys buildings and infrastructure",
            requirements=JobRequirement(
                min_skills={"Design": 50, "Architecture": 40},
                required_tools=["drafting_tools"],
                workspace_type="office",
                min_stats={"Intelligence": 40, "Focus": 30}
            ),
            products=[
                JobProduct(
                    resource_type="building_plan",
                    base_quantity=1.0,
                    quality_factors={"Design": 0.6, "Architecture": 0.4}
                )
            ],
            base_wage=10.0,
            skill_experience={
                "Design": 0.5,
                "Architecture": 0.8,
                "Engineering": 0.3
            },
            work_hours=(8, 16),  # 8 AM to 4 PM
            stress_factor=0.4,
            social_factor=0.6,
            danger_level=0.1
        )
        
        jobs["stonemason"] = Job(
            name="Stonemason",
            category=JobCategory.CONSTRUCTION,
            description="Carves and lays stone for structures and roads",
            requirements=JobRequirement(
                min_skills={"Masonry": 30, "Strength": 40},
                required_tools=["chisel", "hammer"],
                workspace_type="quarry",
                min_stats={"Strength": 50, "Dexterity": 30}
            ),
            products=[
                JobProduct(
                    resource_type="stone_block",
                    base_quantity=5.0,
                    quality_factors={"Masonry": 0.7, "Strength": 0.3}
                )
            ],
            base_wage=8.0,
            skill_experience={
                "Masonry": 1.0,
                "Strength": 0.5,
                "Crafting": 0.2
            },
            work_hours=(6, 14),  # 6 AM to 2 PM
            stress_factor=0.6,
            social_factor=0.3,
            danger_level=0.4
        )
        
        # Farming & Resource Gathering Jobs
        jobs["farmer"] = Job(
            name="Farmer",
            category=JobCategory.FARMING,
            description="Grows crops and manages food production",
            requirements=JobRequirement(
                min_skills={"Farming": 20},
                required_tools=["hoe", "watering_can"],
                workspace_type="field",
                min_stats={"Stamina": 30}
            ),
            products=[
                JobProduct(
                    resource_type="crop",
                    base_quantity=10.0,
                    quality_factors={"Farming": 0.8, "Weather": 0.2}
                )
            ],
            base_wage=6.0,
            skill_experience={
                "Farming": 1.0,
                "Botany": 0.3,
                "Weather_Sense": 0.2
            },
            work_hours=(5, 13),  # 5 AM to 1 PM
            stress_factor=0.3,
            social_factor=0.2,
            danger_level=0.1
        )
        
        # Add more jobs...
        
        return jobs

    def assign_job(self, entity_id: int, job_name: str) -> bool:
        """Attempt to assign a job to an entity"""
        if job_name not in self.jobs:
            return False
            
        job = self.jobs[job_name]
        
        # Check if entity meets requirements
        if not self._check_job_requirements(entity_id, job):
            return False
            
        # Assign job
        self.active_workers[entity_id] = job_name
        return True

    def _check_job_requirements(self, entity_id: int, job: Job) -> bool:
        """Check if an entity meets job requirements"""
        entity = self._get_entity(entity_id)
        if not entity:
            return False
            
        # Check skills
        for skill, level in job.requirements.min_skills.items():
            if skill not in entity.skills or entity.skills[skill] < level:
                return False
                
        # Check stats
        for stat, level in job.requirements.min_stats.items():
            if stat not in entity.stats or entity.stats[stat] < level:
                return False
                
        # Check tools
        for tool in job.requirements.required_tools:
            if tool not in entity.inventory:
                return False
                
        return True

    def update(self, current_time) -> None:
        """Update all job-related activities"""
        hour = current_time.hour
        
        for entity_id, job_name in list(self.active_workers.items()):
            job = self.jobs[job_name]
            
            # Check work hours
            if job.work_hours[0] <= hour < job.work_hours[1]:
                self._process_work(entity_id, job)
            else:
                # Outside work hours
                self._end_work_day(entity_id, job)

    def _process_work(self, entity_id: int, job: Job) -> None:
        """Process work activities for an entity"""
        entity = self._get_entity(entity_id)
        if not entity:
            return
            
        # Apply stress and social effects
        entity.needs["STRESS"] += job.stress_factor
        entity.needs["SOCIAL"] += job.social_factor
        
        # Generate products
        for product in job.products:
            quality = self._calculate_product_quality(entity, product)
            quantity = product.base_quantity * quality
            
            # Add to entity's inventory or workplace storage
            # (Implementation depends on inventory system)
            
        # Grant experience
        for skill, amount in job.skill_experience.items():
            if skill in entity.skills:
                entity.skills[skill] += amount
            else:
                entity.skills[skill] = amount
                
        # Pay wages
        self._pay_wages(entity, job)

    def _calculate_product_quality(self, entity, product: JobProduct) -> float:
        """Calculate the quality of produced goods"""
        quality = 0.0
        total_weight = 0.0
        
        for factor, weight in product.quality_factors.items():
            if factor in entity.skills:
                quality += entity.skills[factor] * weight
            elif factor in entity.stats:
                quality += entity.stats[factor] * weight
            total_weight += weight
            
        return quality / total_weight if total_weight > 0 else 0.5

    def _pay_wages(self, entity, job: Job) -> None:
        """Pay wages to an entity"""
        # Calculate actual wage based on skill and performance
        skill_bonus = sum(entity.skills.get(skill, 0) 
                         for skill in job.requirements.min_skills.keys())
        skill_bonus /= len(job.requirements.min_skills)
        
        wage = job.base_wage * (1 + skill_bonus / 100)
        
        # Add to entity's currency
        entity.currency = getattr(entity, 'currency', 0) + wage

    def _end_work_day(self, entity_id: int, job: Job) -> None:
        """Handle end of work day procedures"""
        entity = self._get_entity(entity_id)
        if not entity:
            return
            
        # Reset work-related states
        entity.needs["STRESS"] = max(0, entity.needs["STRESS"] - 10)
        
        # Add work memories
        entity.add_memory(
            "work",
            f"Completed a day's work as {job.name}",
            0.5
        )

    def get_available_jobs(self, entity_id: int) -> List[str]:
        """Get list of jobs an entity qualifies for"""
        available = []
        entity = self._get_entity(entity_id)
        if not entity:
            return available
            
        for job_name, job in self.jobs.items():
            if self._check_job_requirements(entity_id, job):
                available.append(job_name)
                
        return available

    def add_workplace(self, job_name: str, position: Tuple[int, int]) -> None:
        """Register a new workplace location for a job"""
        if job_name not in self.workplaces:
            self.workplaces[job_name] = []
        self.workplaces[job_name].append(position)

    def get_nearest_workplace(self, job_name: str, 
                            position: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Find the nearest workplace for a job"""
        if job_name not in self.workplaces:
            return None
            
        return min(
            self.workplaces[job_name],
            key=lambda wp: ((wp[0] - position[0])**2 + 
                          (wp[1] - position[1])**2)**0.5,
            default=None
        )

    def _get_entity(self, entity_id: int) -> Optional[object]:
        """Get entity from entity manager (implementation depends on structure)"""
        # This would need to be implemented based on how entities are stored
        pass
