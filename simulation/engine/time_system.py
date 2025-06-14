from dataclasses import dataclass
from typing import Tuple
from .config import TimeOfDay, Month, Weekday, Config

@dataclass
class GameTime:
    """Represents a specific point in time in the game world"""
    minute: int = 0
    hour: int = 6  # Start at 6 AM
    day: int = 1
    month: int = 1
    year: int = 1

    def copy(self) -> 'GameTime':
        """Create a copy of the current time"""
        return GameTime(
            minute=self.minute,
            hour=self.hour,
            day=self.day,
            month=self.month,
            year=self.year
        )

class TimeSystem:
    """
    Manages the passage of time in the game world, including the custom calendar system.
    Features:
    - Custom calendar with 10-day weeks and 300-day years
    - Time of day periods (Firstlight, Highsun, Duskbloom, Starveil)
    - Month and season tracking
    """
    def __init__(self, config: Config):
        self.config = config
        self.current_time = GameTime()
        self.time_multiplier = 1.0  # Can be adjusted to speed up/slow down time
        self.paused = False
        
        # Time thresholds for different periods
        self.TIME_PERIODS = {
            TimeOfDay.FIRSTLIGHT: (6, 11),   # 6 AM - 11 AM
            TimeOfDay.HIGHSUN: (12, 16),     # 12 PM - 4 PM
            TimeOfDay.DUSKBLOOM: (17, 22),   # 5 PM - 10 PM
            TimeOfDay.STARVEIL: (23, 5)      # 11 PM - 5 AM
        }

    def update(self) -> None:
        """Update the current time by one minute"""
        if self.paused:
            return

        self.current_time.minute += int(1 * self.time_multiplier)

        # Handle minute rollover
        if self.current_time.minute >= self.config.TIME.MINUTES_PER_HOUR:
            self.current_time.minute = 0
            self.current_time.hour += 1

            # Handle hour rollover
            if self.current_time.hour >= self.config.TIME.HOURS_PER_DAY:
                self.current_time.hour = 0
                self.current_time.day += 1

                # Handle day rollover
                if self.current_time.day > self.config.TIME.DAYS_PER_MONTH:
                    self.current_time.day = 1
                    self.current_time.month += 1

                    # Handle month rollover
                    if self.current_time.month > self.config.TIME.MONTHS_PER_YEAR:
                        self.current_time.month = 1
                        self.current_time.year += 1

    def get_time_of_day(self) -> TimeOfDay:
        """Get the current time period (Firstlight, Highsun, etc.)"""
        hour = self.current_time.hour
        
        for period, (start, end) in self.TIME_PERIODS.items():
            if period == TimeOfDay.STARVEIL:
                # Special case for period that crosses midnight
                if hour >= start or hour <= end:
                    return period
            elif start <= hour <= end:
                return period
                
        return TimeOfDay.STARVEIL  # Default to night if no match

    def get_current_month(self) -> Month:
        """Get the current month as an enum value"""
        return Month(list(Month)[self.current_time.month - 1].value)

    def get_weekday(self) -> Weekday:
        """Calculate the current weekday based on total days elapsed"""
        total_days = (
            (self.current_time.year - 1) * self.config.TIME.DAYS_PER_YEAR +
            (self.current_time.month - 1) * self.config.TIME.DAYS_PER_MONTH +
            self.current_time.day
        )
        weekday_index = (total_days - 1) % self.config.TIME.DAYS_PER_WEEK
        return Weekday(list(Weekday)[weekday_index].value)

    def get_season(self) -> str:
        """Get the current season based on month"""
        month = self.get_current_month()
        
        if month in [Month.BRIGIDE, Month.IMBOLKA, Month.HIBERNIS, Month.YULITH]:
            return "Winter"
        elif month in [Month.FLORALIS]:
            return "Spring"
        elif month in [Month.LITHARA, Month.HELIAX, Month.AESTIUM]:
            return "Summer"
        else:  # MABONEL, CERESIO
            return "Autumn"

    def get_time_string(self) -> str:
        """Get a formatted string representation of the current time"""
        period = self.get_time_of_day()
        weekday = self.get_weekday()
        month = self.get_current_month()
        
        return (
            f"Year {self.current_time.year}, {month.value} "
            f"{self.current_time.day} ({weekday.value})\n"
            f"{period.value} - {self.current_time.hour:02d}:"
            f"{self.current_time.minute:02d}"
        )

    def is_daytime(self) -> bool:
        """Check if it's currently daytime"""
        period = self.get_time_of_day()
        return period in [TimeOfDay.FIRSTLIGHT, TimeOfDay.HIGHSUN, TimeOfDay.DUSKBLOOM]

    def get_day_progress(self) -> float:
        """Get the progress through the current day as a float between 0 and 1"""
        minutes_in_day = self.config.TIME.HOURS_PER_DAY * self.config.TIME.MINUTES_PER_HOUR
        current_minutes = (self.current_time.hour * self.config.TIME.MINUTES_PER_HOUR + 
                         self.current_time.minute)
        return current_minutes / minutes_in_day

    def get_year_progress(self) -> float:
        """Get the progress through the current year as a float between 0 and 1"""
        days_elapsed = (
            (self.current_time.month - 1) * self.config.TIME.DAYS_PER_MONTH +
            self.current_time.day
        )
        return days_elapsed / self.config.TIME.DAYS_PER_YEAR

    def set_time_multiplier(self, multiplier: float) -> None:
        """Set how fast time passes (1.0 = normal, 2.0 = twice as fast, etc.)"""
        self.time_multiplier = max(0.0, multiplier)

    def toggle_pause(self) -> None:
        """Toggle the pause state of the time system"""
        self.paused = not self.paused
