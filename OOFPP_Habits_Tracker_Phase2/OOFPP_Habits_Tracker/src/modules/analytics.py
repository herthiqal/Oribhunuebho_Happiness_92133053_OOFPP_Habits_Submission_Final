"""
Analytics Module - Functional Programming implementation
Provides analysis functions for habit tracking data
"""
from typing import List, Callable, Dict, Optional
from functools import reduce
from .habit import Habit


# Pure functions for habit analysis using functional programming paradigm

def get_all_tracked_habits(habits: List[Habit]) -> List[str]:
    """
    Return a list of all currently tracked habit names.
    
    Args:
        habits: List of Habit objects
        
    Returns:
        List of habit names
    """
    return list(map(lambda h: h.name, habits))


def filter_by_periodicity(habits: List[Habit], periodicity: str) -> List[Habit]:
    """
    Return habits with the specified periodicity.
    
    Args:
        habits: List of Habit objects
        periodicity: Either 'daily' or 'weekly'
        
    Returns:
        Filtered list of habits
    """
    return list(filter(lambda h: h.periodicity == periodicity, habits))


def get_longest_streak_all_habits(habits: List[Habit]) -> int:
    """
    Return the longest streak across all habits.
    
    Args:
        habits: List of Habit objects
        
    Returns:
        Maximum streak value, or 0 if no habits exist
    """
    if not habits:
        return 0
    
    # Map each habit to its longest streak, then reduce to find maximum
    streaks = map(lambda h: h.get_longest_streak(), habits)
    return reduce(lambda a, b: max(a, b), streaks, 0)


def get_longest_streak_for_habit(habit: Habit) -> int:
    """
    Return the longest streak for a specific habit.
    
    Args:
        habit: Habit object
        
    Returns:
        Longest streak value
    """
    return habit.get_longest_streak()


def get_habit_with_longest_streak(habits: List[Habit]) -> Optional[Habit]:
    """
    Find the habit with the longest overall streak.
    
    Args:
        habits: List of Habit objects
        
    Returns:
        Habit with longest streak, or None if no habits
    """
    if not habits:
        return None
    
    return reduce(
        lambda h1, h2: h1 if h1.get_longest_streak() >= h2.get_longest_streak() else h2,
        habits
    )


def calculate_completion_rate(habit: Habit, days: int = 30) -> float:
    """
    Calculate completion rate for a habit over the last N days.
    
    Args:
        habit: Habit object
        days: Number of days to analyze
        
    Returns:
        Completion rate as percentage (0-100)
    """
    from datetime import datetime, timedelta
    
    if habit.periodicity != 'daily':
        # For weekly habits, calculate based on weeks
        weeks = days // 7
        if weeks == 0:
            return 0.0
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_completions = list(filter(
            lambda c: c >= cutoff_date,
            habit.completions
        ))
        
        # Count unique weeks with completions
        weeks_completed = len(set(
            (c.date() - timedelta(days=c.weekday())) 
            for c in recent_completions
        ))
        
        return (weeks_completed / weeks) * 100
    
    else:
        # For daily habits
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_completions = list(filter(
            lambda c: c >= cutoff_date,
            habit.completions
        ))
        
        # Count unique days with completions
        days_completed = len(set(c.date() for c in recent_completions))
        return (days_completed / days) * 100


def get_struggling_habits(habits: List[Habit], threshold: float = 50.0) -> List[Habit]:
    """
    Identify habits with completion rate below threshold.
    
    Args:
        habits: List of Habit objects
        threshold: Minimum acceptable completion rate
        
    Returns:
        List of habits struggling to maintain consistency
    """
    return list(filter(
        lambda h: calculate_completion_rate(h) < threshold,
        habits
    ))


def get_active_habits(habits: List[Habit]) -> List[Habit]:
    """
    Return habits that are not currently broken.
    
    Args:
        habits: List of Habit objects
        
    Returns:
        List of active (non-broken) habits
    """
    return list(filter(lambda h: not h.is_broken(), habits))


def get_broken_habits(habits: List[Habit]) -> List[Habit]:
    """
    Return habits that are currently broken.
    
    Args:
        habits: List of Habit objects
        
    Returns:
        List of broken habits
    """
    return list(filter(lambda h: h.is_broken(), habits))


def calculate_total_completions(habits: List[Habit]) -> int:
    """
    Calculate total number of completions across all habits.
    
    Args:
        habits: List of Habit objects
        
    Returns:
        Total completion count
    """
    return reduce(
        lambda total, h: total + len(h.completions),
        habits,
        0
    )


def get_habits_summary(habits: List[Habit]) -> Dict[str, any]:
    """
    Generate a comprehensive summary of all habits.
    
    Args:
        habits: List of Habit objects
        
    Returns:
        Dictionary with summary statistics
    """
    if not habits:
        return {
            'total_habits': 0,
            'daily_habits': 0,
            'weekly_habits': 0,
            'active_habits': 0,
            'broken_habits': 0,
            'total_completions': 0,
            'longest_streak': 0,
            'average_streak': 0.0
        }
    
    daily = filter_by_periodicity(habits, 'daily')
    weekly = filter_by_periodicity(habits, 'weekly')
    active = get_active_habits(habits)
    broken = get_broken_habits(habits)
    
    # Calculate average current streak
    current_streaks = list(map(lambda h: h.get_current_streak(), habits))
    avg_streak = sum(current_streaks) / len(current_streaks) if current_streaks else 0.0
    
    return {
        'total_habits': len(habits),
        'daily_habits': len(daily),
        'weekly_habits': len(weekly),
        'active_habits': len(active),
        'broken_habits': len(broken),
        'total_completions': calculate_total_completions(habits),
        'longest_streak': get_longest_streak_all_habits(habits),
        'average_streak': round(avg_streak, 2)
    }


def sort_habits_by_streak(habits: List[Habit], descending: bool = True) -> List[Habit]:
    """
    Sort habits by their current streak.
    
    Args:
        habits: List of Habit objects
        descending: If True, sort from highest to lowest
        
    Returns:
        Sorted list of habits
    """
    return sorted(
        habits,
        key=lambda h: h.get_current_streak(),
        reverse=descending
    )


def compose(*functions: Callable) -> Callable:
    """
    Compose multiple functions together (functional programming pattern).
    
    Args:
        *functions: Variable number of functions to compose
        
    Returns:
        Composed function
    """
    return reduce(
        lambda f, g: lambda x: f(g(x)),
        functions,
        lambda x: x
    )


# Example of function composition
def get_top_performing_daily_habits(habits: List[Habit], limit: int = 5) -> List[Habit]:
    """
    Get top N daily habits sorted by streak.
    Demonstrates function composition in FP.
    
    Args:
        habits: List of Habit objects
        limit: Number of habits to return
        
    Returns:
        Top performing daily habits
    """
    daily_habits = filter_by_periodicity(habits, 'daily')
    sorted_habits = sort_habits_by_streak(daily_habits)
    return sorted_habits[:limit]
