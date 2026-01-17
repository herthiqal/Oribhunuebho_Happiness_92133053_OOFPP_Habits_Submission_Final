"""
Habit class - Object-Oriented Programming implementation
Represents a single habit with its properties and methods
"""
from datetime import datetime, timedelta
from typing import List, Optional


class Habit:
    """
    Represents a trackable habit with a specific task and periodicity.
    
    Attributes:
        name (str): The name/description of the habit
        periodicity (str): How often the habit should be completed ('daily' or 'weekly')
        created_at (datetime): When the habit was created
        habit_id (int): Unique identifier for the habit
    """
    
    def __init__(self, name: str, periodicity: str, created_at: Optional[datetime] = None, habit_id: Optional[int] = None):
        """
        Initialize a new Habit instance.
        
        Args:
            name: The habit's name/task description
            periodicity: Either 'daily' or 'weekly'
            created_at: Creation timestamp (defaults to now)
            habit_id: Unique ID (assigned by database)
        """
        self.name = name
        self.periodicity = periodicity.lower()
        self.created_at = created_at or datetime.now()
        self.habit_id = habit_id
        self.completions: List[datetime] = []
        
        # Validate periodicity
        if self.periodicity not in ['daily', 'weekly']:
            raise ValueError("Periodicity must be 'daily' or 'weekly'")
    
    def add_completion(self, completion_date: Optional[datetime] = None) -> None:
        """
        Add a completion record for this habit.
        
        Args:
            completion_date: When the habit was completed (defaults to now)
        """
        date = completion_date or datetime.now()
        self.completions.append(date)
        self.completions.sort()  # Keep sorted for streak calculations
    
    def get_current_streak(self) -> int:
        """
        Calculate the current streak of consecutive completions.
        
        Returns:
            Number of consecutive periods completed (ending with most recent period)
        """
        if not self.completions:
            return 0
        
        now = datetime.now()
        streak = 0
        
        if self.periodicity == 'daily':
            # Check each day going backwards
            check_date = now.date()
            for i in range(len(self.completions)):
                # Check if we completed the habit on check_date
                if any(c.date() == check_date for c in self.completions):
                    streak += 1
                    check_date -= timedelta(days=1)
                else:
                    break
        else:  # weekly
            # Get the start of current week (Monday)
            today = now.date()
            days_since_monday = today.weekday()
            check_week_start = today - timedelta(days=days_since_monday)
            
            # Check each week going backwards
            for i in range(len(self.completions)):
                week_end = check_week_start + timedelta(days=6)
                # Check if we completed the habit in this week
                if any(check_week_start <= c.date() <= week_end for c in self.completions):
                    streak += 1
                    check_week_start -= timedelta(days=7)
                else:
                    break
        
        return streak
    
    def get_longest_streak(self) -> int:
        """
        Calculate the longest streak ever achieved for this habit.
        
        Returns:
            Maximum number of consecutive periods completed
        """
        if not self.completions:
            return 0
        
        max_streak = 0
        current_streak = 0
        
        if self.periodicity == 'daily':
            # Sort completions and check for consecutive days
            dates = sorted(set(c.date() for c in self.completions))
            
            for i, date in enumerate(dates):
                if i == 0:
                    current_streak = 1
                else:
                    # Check if this is consecutive to previous date
                    if (date - dates[i-1]).days == 1:
                        current_streak += 1
                    else:
                        current_streak = 1
                
                max_streak = max(max_streak, current_streak)
        
        else:  # weekly
            # Group completions by week
            weeks = set()
            for completion in self.completions:
                week_start = completion.date() - timedelta(days=completion.weekday())
                weeks.add(week_start)
            
            sorted_weeks = sorted(weeks)
            
            for i, week in enumerate(sorted_weeks):
                if i == 0:
                    current_streak = 1
                else:
                    # Check if this is consecutive week
                    if (week - sorted_weeks[i-1]).days == 7:
                        current_streak += 1
                    else:
                        current_streak = 1
                
                max_streak = max(max_streak, current_streak)
        
        return max_streak
    
    def is_broken(self) -> bool:
        """
        Check if the habit streak is currently broken.
        
        Returns:
            True if the habit should have been completed but wasn't
        """
        if not self.completions:
            # If no completions, check if enough time has passed since creation
            if self.periodicity == 'daily':
                return (datetime.now() - self.created_at).days >= 1
            else:  # weekly
                return (datetime.now() - self.created_at).days >= 7
        
        last_completion = self.completions[-1]
        now = datetime.now()
        
        if self.periodicity == 'daily':
            # Should have completed at least once since yesterday
            return (now.date() - last_completion.date()).days > 1
        else:  # weekly
            # Check if we're in a different week and haven't completed
            last_week_start = last_completion.date() - timedelta(days=last_completion.weekday())
            current_week_start = now.date() - timedelta(days=now.weekday())
            weeks_diff = (current_week_start - last_week_start).days // 7
            return weeks_diff > 1
    
    def to_dict(self) -> dict:
        """
        Convert habit to dictionary format.
        
        Returns:
            Dictionary representation of the habit
        """
        return {
            'id': self.habit_id,
            'name': self.name,
            'periodicity': self.periodicity,
            'created_at': self.created_at.isoformat(),
            'current_streak': self.get_current_streak(),
            'longest_streak': self.get_longest_streak(),
            'is_broken': self.is_broken(),
            'total_completions': len(self.completions)
        }
    
    def __repr__(self) -> str:
        """String representation of the habit."""
        return f"Habit(name='{self.name}', periodicity='{self.periodicity}', streak={self.get_current_streak()})"
    
    def __str__(self) -> str:
        """User-friendly string representation."""
        status = "✓" if not self.is_broken() else "✗"
        return f"{status} {self.name} ({self.periodicity}) - Streak: {self.get_current_streak()}"
