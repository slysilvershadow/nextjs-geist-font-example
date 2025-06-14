from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple

class TimeOfDay(Enum):
    FIRSTLIGHT = "Firstlight"  # 6 AM - 11 AM
    HIGHSUN = "Highsun"      # 12 PM - 4 PM
    DUSKBLOOM = "Duskbloom"  # 5 PM - 10 PM
    STARVEIL = "Starveil"    # 11 PM - 5 AM

class Month(Enum):
    BRIGIDE = "Brigide"     # Winter
    IMBOLKA = "Imbolka"     # Late Winter
    FLORALIS = "Floralis"   # Spring
    LITHARA = "Lithara"     # Early Summer
    HELIAX = "Heliax"       # Midsummer
    AESTIUM = "Aestium"     # Late Summer
    MABONEL = "Mabonel"     # Autumn
    CERESIO = "Ceresio"     # Late Autumn
    YULITH = "Yulith"       # Early Winter
    HIBERNIS = "Hibernis"   # Mid-Winter

class Weekday(Enum):
    SOLTHOS = "Solthos"
    MORTHOS = "Morthos"
    BLAZTHOS = "Blazthos"
    FENTHOS = "Fenthos"
    CYNTHOS = "Cynthos"
    CALTHOS = "Calthos"
    ASTRATHOS = "Astrathos"
    WISPTHOS = "Wispthos"
    HELIOTHOS = "Heliothos"
    ETHOTHOS = "Ethothos"

@dataclass
class TimeConfig:
    MINUTES_PER_HOUR: int = 60
    HOURS_PER_DAY: int = 24
    DAYS_PER_WEEK: int = 10
    DAYS_PER_MONTH: int = 30
    MONTHS_PER_YEAR: int = 10
    DAYS_PER_YEAR: int = 300

@dataclass
class WorldConfig:
    TILE_SIZE: int = 32
    CHUNK_SIZE: int = 16
    WORLD_WIDTH: int = 100
    WORLD_HEIGHT: int = 100
    MIN_TEMPERATURE: float = -50.0
    MAX_TEMPERATURE: float = 45.0

@dataclass
class DisplayConfig:
    SCREEN_WIDTH: int = 1024
    SCREEN_HEIGHT: int = 768
    FPS: int = 60
    ZOOM_LEVELS: List[float] = (0.5, 1.0, 2.0)
    DEFAULT_ZOOM: float = 1.0

@dataclass
class Config:
    """Main configuration class that holds all settings"""
    def __init__(self):
        self.TIME = TimeConfig()
        self.WORLD = WorldConfig()
        self.DISPLAY = DisplayConfig()
        
        # Biome temperature and moisture thresholds
        self.BIOME_THRESHOLDS = {
            "BOREAL_FOREST": {"temp": (-10, 15), "moisture": (0.4, 0.6), "elevation": (200, 1500)},
            "DECIDUOUS_FOREST": {"temp": (0, 25), "moisture": (0.5, 0.8), "elevation": (0, 1200)},
            "RAINFOREST": {"temp": (24, 30), "moisture": (0.8, 1.0), "elevation": (0, 1000)},
            "TUNDRA": {"temp": (-30, 5), "moisture": (0.2, 0.5), "elevation": (0, 1000)},
            "STEPPE": {"temp": (-5, 25), "moisture": (0.2, 0.4), "elevation": (200, 1500)},
            "SAVANNA": {"temp": (20, 30), "moisture": (0.3, 0.6), "elevation": (0, 1200)},
            "POLAR_DESERT": {"temp": (-50, 0), "moisture": (0.0, 0.2), "elevation": (0, 3000)},
            "SEMI_ARID_DESERT": {"temp": (-5, 20), "moisture": (0.1, 0.3), "elevation": (500, 2000)},
            "SAND_DESERT": {"temp": (20, 45), "moisture": (0.0, 0.15), "elevation": (0, 1000)},
            "HEATH": {"temp": (5, 20), "moisture": (0.4, 0.7), "elevation": (100, 1000)},
            "CHAPARRAL": {"temp": (10, 30), "moisture": (0.3, 0.5), "elevation": (100, 1200)},
            "SWAMP": {"temp": (5, 30), "moisture": (0.7, 1.0), "elevation": (0, 200)}
        }

        # Stat decay rates and thresholds
        self.NEEDS_CONFIG = {
            "HEALTH": {"min": 0, "max": 100, "decay": 0.0, "priority": 1},
            "THIRST": {"min": 0, "max": 100, "decay": 0.1, "priority": 2},
            "HUNGER": {"min": 0, "max": 100, "decay": 0.05, "priority": 3},
            "ENERGY": {"min": 0, "max": 100, "decay": 0.04, "priority": 6},
            "SOCIAL": {"min": -100, "max": 100, "decay": 0.02, "priority": 15}
        }

        # Base skill progression rates
        self.SKILL_CONFIG = {
            "BASE_XP_GAIN": 1.0,
            "LEVEL_MULTIPLIER": 1.5,
            "MAX_LEVEL": 100,
            "DECAY_RATE": 0.02
        }

        # Screen dimensions and display settings
        self.SCREEN_WIDTH = self.DISPLAY.SCREEN_WIDTH
        self.SCREEN_HEIGHT = self.DISPLAY.SCREEN_HEIGHT
        self.FPS = self.DISPLAY.FPS
