"""
Seed Database Script
Creates 5 predefined habits with 4 weeks of sample tracking data
"""
from datetime import datetime, timedelta
import random
from src.modules.habit import Habit
from src.modules.database import DatabaseManager


def seed_database(db_path: str = "habits.db"):
    """
    Create sample habits with 4 weeks of tracking data.
    
    This creates:
    - 3 daily habits
    - 2 weekly habits
    - Realistic completion patterns showing various streak behaviors
    """
    db = DatabaseManager(db_path)
    
    # Define 5 predefined habits
    habits_data = [
        {"name": "Morning Exercise", "periodicity": "daily"},
        {"name": "Read for 30 minutes", "periodicity": "daily"},
        {"name": "Drink 8 glasses of water", "periodicity": "daily"},
        {"name": "Grocery Shopping", "periodicity": "weekly"},
        {"name": "Review Weekly Goals", "periodicity": "weekly"}
    ]
    
    print("🌱 Seeding database with sample habits...")
    
    # Create habits and add 4 weeks of tracking data
    now = datetime.now()
    four_weeks_ago = now - timedelta(weeks=4)
    
    for habit_data in habits_data:
        # Create habit with creation date 4 weeks ago
        habit = Habit(
            name=habit_data["name"],
            periodicity=habit_data["periodicity"],
            created_at=four_weeks_ago
        )
        
        # Save habit to database
        habit_id = db.save_habit(habit)
        print(f"✓ Created habit: {habit.name} ({habit.periodicity})")
        
        # Generate completion data based on periodicity
        if habit.periodicity == "daily":
            # Generate daily completions with realistic patterns
            # Different habits have different completion rates
            completion_rate = random.uniform(0.6, 0.95)  # 60-95% completion rate
            
            for day in range(28):  # 4 weeks = 28 days
                completion_date = four_weeks_ago + timedelta(days=day)
                
                # Randomly decide if completed based on rate
                if random.random() < completion_rate:
                    db.add_completion(habit_id, completion_date)
                    
                # Simulate "perfect weeks" - higher completion on certain weeks
                week_num = day // 7
                if week_num in [1, 3]:  # Weeks 2 and 4 are better
                    if random.random() < 0.15:  # Extra 15% chance
                        if not any(c.date() == completion_date.date() 
                                 for c in db.get_completions(habit_id)):
                            db.add_completion(habit_id, completion_date)
        
        else:  # weekly habits
            # For weekly habits, complete once per week with some misses
            completion_rate = random.uniform(0.7, 1.0)  # 70-100% of weeks
            
            for week in range(4):
                # Complete sometime during the week
                if random.random() < completion_rate:
                    # Random day in that week
                    day_in_week = random.randint(0, 6)
                    completion_date = four_weeks_ago + timedelta(days=week*7 + day_in_week)
                    db.add_completion(habit_id, completion_date)
        
        # Show completion stats
        habit_reloaded = db.get_habit(habit_id)
        print(f"  → {len(habit_reloaded.completions)} completions over 4 weeks")
        print(f"  → Current streak: {habit_reloaded.get_current_streak()}")
        print(f"  → Longest streak: {habit_reloaded.get_longest_streak()}")
        print()
    
    db.close()
    print("✅ Database seeded successfully!")
    print(f"📁 Database location: {db_path}")
    print("\nYou can now run the application with: python main.py")


if __name__ == "__main__":
    # Ask user for confirmation before seeding
    print("This script will create sample habits with 4 weeks of tracking data.")
    response = input("Proceed? (yes/no): ").strip().lower()
    
    if response == 'yes':
        seed_database()
    else:
        print("Operation cancelled.")
