"""
Database Manager - Handles all SQLite operations for habit persistence
"""
import sqlite3
from datetime import datetime
from typing import List, Optional
from .habit import Habit


class DatabaseManager:
    """
    Manages SQLite database operations for habit tracking.
    Handles creation, storage, and retrieval of habits and completions.
    """
    
    def __init__(self, db_path: str = "habits.db"):
        """
        Initialize database connection and create tables if needed.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row  # Enable dict-like access
        self._create_tables()
    
    def _create_tables(self) -> None:
        """Create the necessary database tables if they don't exist."""
        cursor = self.connection.cursor()
        
        # Habits table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                periodicity TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Completions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL,
                completed_at TEXT NOT NULL,
                FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE
            )
        ''')
        
        # Create index for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_habit_completions 
            ON completions(habit_id, completed_at)
        ''')
        
        self.connection.commit()
    
    def save_habit(self, habit: Habit) -> int:
        """
        Save a new habit to the database.
        
        Args:
            habit: Habit object to save
            
        Returns:
            The ID of the newly created habit
        """
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO habits (name, periodicity, created_at)
            VALUES (?, ?, ?)
        ''', (habit.name, habit.periodicity, habit.created_at.isoformat()))
        
        self.connection.commit()
        habit.habit_id = cursor.lastrowid
        return cursor.lastrowid
    
    def update_habit(self, habit: Habit) -> None:
        """
        Update an existing habit in the database.
        
        Args:
            habit: Habit object with updated information
        """
        cursor = self.connection.cursor()
        cursor.execute('''
            UPDATE habits 
            SET name = ?, periodicity = ?
            WHERE id = ?
        ''', (habit.name, habit.periodicity, habit.habit_id))
        
        self.connection.commit()
    
    def delete_habit(self, habit_id: int) -> bool:
        """
        Delete a habit and all its completions.
        
        Args:
            habit_id: ID of the habit to delete
            
        Returns:
            True if habit was deleted, False if not found
        """
        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM habits WHERE id = ?', (habit_id,))
        deleted = cursor.rowcount > 0
        self.connection.commit()
        return deleted
    
    def get_habit(self, habit_id: int) -> Optional[Habit]:
        """
        Retrieve a habit by its ID.
        
        Args:
            habit_id: ID of the habit to retrieve
            
        Returns:
            Habit object or None if not found
        """
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM habits WHERE id = ?', (habit_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        habit = Habit(
            name=row['name'],
            periodicity=row['periodicity'],
            created_at=datetime.fromisoformat(row['created_at']),
            habit_id=row['id']
        )
        
        # Load completions
        habit.completions = self.get_completions(habit_id)
        return habit
    
    def get_all_habits(self) -> List[Habit]:
        """
        Retrieve all habits from the database.
        
        Returns:
            List of all Habit objects
        """
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM habits ORDER BY created_at DESC')
        rows = cursor.fetchall()
        
        habits = []
        for row in rows:
            habit = Habit(
                name=row['name'],
                periodicity=row['periodicity'],
                created_at=datetime.fromisoformat(row['created_at']),
                habit_id=row['id']
            )
            habit.completions = self.get_completions(row['id'])
            habits.append(habit)
        
        return habits
    
    def get_habits_by_periodicity(self, periodicity: str) -> List[Habit]:
        """
        Retrieve all habits with a specific periodicity.
        
        Args:
            periodicity: Either 'daily' or 'weekly'
            
        Returns:
            List of matching Habit objects
        """
        cursor = self.connection.cursor()
        cursor.execute(
            'SELECT * FROM habits WHERE periodicity = ? ORDER BY created_at DESC',
            (periodicity,)
        )
        rows = cursor.fetchall()
        
        habits = []
        for row in rows:
            habit = Habit(
                name=row['name'],
                periodicity=row['periodicity'],
                created_at=datetime.fromisoformat(row['created_at']),
                habit_id=row['id']
            )
            habit.completions = self.get_completions(row['id'])
            habits.append(habit)
        
        return habits
    
    def add_completion(self, habit_id: int, completed_at: Optional[datetime] = None) -> None:
        """
        Record a completion for a habit.
        
        Args:
            habit_id: ID of the habit
            completed_at: When the habit was completed (defaults to now)
        """
        date = completed_at or datetime.now()
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO completions (habit_id, completed_at)
            VALUES (?, ?)
        ''', (habit_id, date.isoformat()))
        
        self.connection.commit()
    
    def get_completions(self, habit_id: int) -> List[datetime]:
        """
        Retrieve all completion dates for a habit.
        
        Args:
            habit_id: ID of the habit
            
        Returns:
            List of completion datetimes
        """
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT completed_at FROM completions 
            WHERE habit_id = ? 
            ORDER BY completed_at
        ''', (habit_id,))
        
        rows = cursor.fetchall()
        return [datetime.fromisoformat(row['completed_at']) for row in rows]
    
    def close(self) -> None:
        """Close the database connection."""
        self.connection.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures connection is closed."""
        self.close()
