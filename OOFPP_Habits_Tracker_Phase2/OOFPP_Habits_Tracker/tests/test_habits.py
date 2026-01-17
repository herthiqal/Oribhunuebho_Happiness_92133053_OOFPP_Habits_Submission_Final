"""
Unit tests for Habit Tracker application
Tests critical functionality using pytest
"""
import pytest
from datetime import datetime, timedelta
from src.modules.habit import Habit
from src.modules.database import DatabaseManager
from src.modules import analytics
import os


# Fixtures

@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    db_path = "test_habits.db"
    db = DatabaseManager(db_path)
    yield db
    db.close()
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def sample_habit():
    """Create a sample habit for testing."""
    return Habit(name="Exercise", periodicity="daily")


@pytest.fixture
def sample_habits():
    """Create a list of sample habits for testing."""
    return [
        Habit(name="Exercise", periodicity="daily"),
        Habit(name="Read", periodicity="daily"),
        Habit(name="Meditate", periodicity="daily"),
        Habit(name="Gym", periodicity="weekly"),
        Habit(name="Review Goals", periodicity="weekly")
    ]


# Tests for Habit class

class TestHabitClass:
    """Test the Habit class functionality."""
    
    def test_habit_creation(self):
        """Test that a habit can be created with valid parameters."""
        habit = Habit(name="Test Habit", periodicity="daily")
        assert habit.name == "Test Habit"
        assert habit.periodicity == "daily"
        assert isinstance(habit.created_at, datetime)
        assert habit.completions == []
    
    def test_invalid_periodicity(self):
        """Test that invalid periodicity raises an error."""
        with pytest.raises(ValueError):
            Habit(name="Test", periodicity="monthly")
    
    def test_add_completion(self, sample_habit):
        """Test adding completions to a habit."""
        sample_habit.add_completion()
        assert len(sample_habit.completions) == 1
        
        # Add another completion
        sample_habit.add_completion()
        assert len(sample_habit.completions) == 2
    
    def test_current_streak_calculation(self, sample_habit):
        """Test current streak calculation for consecutive days."""
        now = datetime.now()
        
        # Add completions for last 3 days
        sample_habit.add_completion(now)
        sample_habit.add_completion(now - timedelta(days=1))
        sample_habit.add_completion(now - timedelta(days=2))
        
        assert sample_habit.get_current_streak() == 3
    
    def test_broken_streak(self, sample_habit):
        """Test that missing a day breaks the streak."""
        now = datetime.now()
        
        # Complete today and 3 days ago (missing yesterday)
        sample_habit.add_completion(now)
        sample_habit.add_completion(now - timedelta(days=3))
        
        # Current streak should only count today
        assert sample_habit.get_current_streak() == 1
    
    def test_longest_streak(self, sample_habit):
        """Test longest streak calculation."""
        now = datetime.now()
        
        # Create a 5-day streak, then break, then 3-day streak
        for i in range(5):
            sample_habit.add_completion(now - timedelta(days=i+7))
        
        for i in range(3):
            sample_habit.add_completion(now - timedelta(days=i))
        
        assert sample_habit.get_longest_streak() == 5
    
    def test_weekly_habit_streak(self):
        """Test streak calculation for weekly habits."""
        habit = Habit(name="Weekly Task", periodicity="weekly")
        now = datetime.now()
        
        # Complete for current week and last week
        habit.add_completion(now)
        habit.add_completion(now - timedelta(days=7))
        
        assert habit.get_current_streak() == 2
    
    def test_is_broken_daily(self):
        """Test if daily habit detects when it's broken."""
        habit = Habit(name="Daily Task", periodicity="daily")
        
        # Complete 3 days ago - should be broken
        habit.add_completion(datetime.now() - timedelta(days=3))
        assert habit.is_broken() == True
    
    def test_is_not_broken(self, sample_habit):
        """Test that recently completed habit is not broken."""
        sample_habit.add_completion(datetime.now())
        assert sample_habit.is_broken() == False


# Tests for DatabaseManager

class TestDatabaseManager:
    """Test database operations."""
    
    def test_save_and_retrieve_habit(self, temp_db):
        """Test saving and retrieving a habit."""
        habit = Habit(name="Test Habit", periodicity="daily")
        habit_id = temp_db.save_habit(habit)
        
        retrieved = temp_db.get_habit(habit_id)
        assert retrieved is not None
        assert retrieved.name == "Test Habit"
        assert retrieved.periodicity == "daily"
    
    def test_get_all_habits(self, temp_db):
        """Test retrieving all habits."""
        habit1 = Habit(name="Habit 1", periodicity="daily")
        habit2 = Habit(name="Habit 2", periodicity="weekly")
        
        temp_db.save_habit(habit1)
        temp_db.save_habit(habit2)
        
        all_habits = temp_db.get_all_habits()
        assert len(all_habits) == 2
    
    def test_delete_habit(self, temp_db):
        """Test deleting a habit."""
        habit = Habit(name="To Delete", periodicity="daily")
        habit_id = temp_db.save_habit(habit)
        
        result = temp_db.delete_habit(habit_id)
        assert result == True
        
        retrieved = temp_db.get_habit(habit_id)
        assert retrieved is None
    
    def test_update_habit(self, temp_db):
        """Test updating a habit."""
        habit = Habit(name="Original Name", periodicity="daily")
        habit_id = temp_db.save_habit(habit)
        
        habit.name = "Updated Name"
        habit.periodicity = "weekly"
        temp_db.update_habit(habit)
        
        retrieved = temp_db.get_habit(habit_id)
        assert retrieved.name == "Updated Name"
        assert retrieved.periodicity == "weekly"
    
    def test_add_completion_to_database(self, temp_db):
        """Test adding and retrieving completions."""
        habit = Habit(name="Test", periodicity="daily")
        habit_id = temp_db.save_habit(habit)
        
        # Add completion
        temp_db.add_completion(habit_id)
        
        # Retrieve and verify
        retrieved = temp_db.get_habit(habit_id)
        assert len(retrieved.completions) == 1
    
    def test_get_habits_by_periodicity(self, temp_db, sample_habits):
        """Test filtering habits by periodicity."""
        for habit in sample_habits:
            temp_db.save_habit(habit)
        
        daily_habits = temp_db.get_habits_by_periodicity('daily')
        weekly_habits = temp_db.get_habits_by_periodicity('weekly')
        
        assert len(daily_habits) == 3
        assert len(weekly_habits) == 2


# Tests for Analytics module

class TestAnalytics:
    """Test analytics functions."""
    
    def test_get_all_tracked_habits(self, sample_habits):
        """Test retrieving all habit names."""
        names = analytics.get_all_tracked_habits(sample_habits)
        assert len(names) == 5
        assert "Exercise" in names
        assert "Gym" in names
    
    def test_filter_by_periodicity(self, sample_habits):
        """Test filtering habits by periodicity."""
        daily = analytics.filter_by_periodicity(sample_habits, 'daily')
        weekly = analytics.filter_by_periodicity(sample_habits, 'weekly')
        
        assert len(daily) == 3
        assert len(weekly) == 2
        assert all(h.periodicity == 'daily' for h in daily)
    
    def test_longest_streak_all_habits(self, sample_habits):
        """Test finding longest streak across all habits."""
        # Add completions to create different streaks
        now = datetime.now()
        for i in range(5):
            sample_habits[0].add_completion(now - timedelta(days=i))
        for i in range(3):
            sample_habits[1].add_completion(now - timedelta(days=i))
        
        longest = analytics.get_longest_streak_all_habits(sample_habits)
        assert longest == 5
    
    def test_get_habit_with_longest_streak(self, sample_habits):
        """Test finding the habit with longest streak."""
        now = datetime.now()
        
        # Give first habit a longer streak
        for i in range(7):
            sample_habits[0].add_completion(now - timedelta(days=i))
        for i in range(3):
            sample_habits[1].add_completion(now - timedelta(days=i))
        
        best_habit = analytics.get_habit_with_longest_streak(sample_habits)
        assert best_habit.name == "Exercise"
        assert best_habit.get_longest_streak() == 7
    
    def test_completion_rate(self):
        """Test completion rate calculation."""
        habit = Habit(name="Test", periodicity="daily")
        now = datetime.now()
        
        # Complete 15 out of last 30 days
        for i in range(15):
            habit.add_completion(now - timedelta(days=i*2))
        
        rate = analytics.calculate_completion_rate(habit, days=30)
        assert rate == 50.0
    
    def test_get_struggling_habits(self, sample_habits):
        """Test identifying struggling habits."""
        now = datetime.now()
        
        # Make first habit have low completion rate
        for i in range(5):
            sample_habits[0].add_completion(now - timedelta(days=i*3))
        
        # Make second habit have high completion rate
        for i in range(25):
            sample_habits[1].add_completion(now - timedelta(days=i))
        
        struggling = analytics.get_struggling_habits(sample_habits, threshold=50.0)
        assert any(h.name == "Exercise" for h in struggling)
        assert not any(h.name == "Read" for h in struggling)
    
    def test_get_active_habits(self, sample_habits):
        """Test filtering active (non-broken) habits."""
        # Make some habits active
        sample_habits[0].add_completion(datetime.now())
        sample_habits[1].add_completion(datetime.now())
        
        active = analytics.get_active_habits(sample_habits)
        assert len(active) >= 2
    
    def test_calculate_total_completions(self, sample_habits):
        """Test calculating total completions across habits."""
        now = datetime.now()
        
        for i in range(5):
            sample_habits[0].add_completion(now - timedelta(days=i))
        for i in range(3):
            sample_habits[1].add_completion(now - timedelta(days=i))
        
        total = analytics.calculate_total_completions(sample_habits)
        assert total == 8
    
    def test_habits_summary(self, sample_habits):
        """Test generating habits summary."""
        now = datetime.now()
        
        # Add some completions
        for habit in sample_habits[:2]:
            for i in range(3):
                habit.add_completion(now - timedelta(days=i))
        
        summary = analytics.get_habits_summary(sample_habits)
        
        assert summary['total_habits'] == 5
        assert summary['daily_habits'] == 3
        assert summary['weekly_habits'] == 2
        assert summary['total_completions'] == 6
        assert isinstance(summary['average_streak'], float)
    
    def test_sort_habits_by_streak(self, sample_habits):
        """Test sorting habits by streak."""
        now = datetime.now()
        
        # Give different streaks
        for i in range(5):
            sample_habits[0].add_completion(now - timedelta(days=i))
        for i in range(2):
            sample_habits[1].add_completion(now - timedelta(days=i))
        
        sorted_habits = analytics.sort_habits_by_streak(sample_habits)
        
        # First should have longest streak
        assert sorted_habits[0].get_current_streak() >= sorted_habits[1].get_current_streak()


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
