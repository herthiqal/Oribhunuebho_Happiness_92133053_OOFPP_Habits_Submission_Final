"""
Main CLI Interface for Habit Tracker
Provides user interaction through command-line interface
"""
from datetime import datetime, timedelta
from modules.habit import Habit
from modules.database import DatabaseManager
from modules import analytics


class HabitTrackerCLI:
    """
    Command-line interface for the Habit Tracker application.
    """
    
    def __init__(self, db_path: str = "habits.db"):
        """Initialize the CLI with database connection."""
        self.db = DatabaseManager(db_path)
        self.running = True
        
    def display_banner(self):
        """Display welcome banner."""
        print("\n" + "="*60)
        print("          🎯 HABIT TRACKER - Build Better Habits 🎯")
        print("="*60)
        print("Type 'help' to see available commands\n")
    
    def display_help(self):
        """Display help menu with all available commands."""
        help_text = """
┌─────────────────────────────────────────────────────────────┐
│                    AVAILABLE COMMANDS                        │
├─────────────────────────────────────────────────────────────┤
│  create          - Create a new habit                        │
│  list            - List all habits                           │
│  complete        - Mark a habit as completed                 │
│  delete          - Delete a habit                            │
│  update          - Update habit details                      │
│  analyze         - View habit analytics                      │
│  summary         - Display overall statistics                │
│  help            - Show this help menu                       │
│  exit            - Exit the application                      │
└─────────────────────────────────────────────────────────────┘
        """
        print(help_text)
    
    def create_habit(self):
        """Create a new habit interactively."""
        print("\n📝 Create New Habit")
        print("-" * 40)
        
        name = input("Enter habit name: ").strip()
        if not name:
            print("❌ Habit name cannot be empty!")
            return
        
        print("\nPeriodicity options:")
        print("  1. Daily")
        print("  2. Weekly")
        choice = input("Select periodicity (1 or 2): ").strip()
        
        periodicity_map = {'1': 'daily', '2': 'weekly'}
        periodicity = periodicity_map.get(choice)
        
        if not periodicity:
            print("❌ Invalid choice!")
            return
        
        try:
            habit = Habit(name=name, periodicity=periodicity)
            self.db.save_habit(habit)
            print(f"\n✅ Habit '{name}' ({periodicity}) created successfully!")
        except Exception as e:
            print(f"❌ Error creating habit: {e}")
    
    def list_habits(self):
        """Display all habits with their current status."""
        habits = self.db.get_all_habits()
        
        if not habits:
            print("\n📭 No habits tracked yet. Create one with 'create' command!")
            return
        
        print("\n📋 Your Habits")
        print("="*80)
        print(f"{'ID':<5} {'Name':<25} {'Period':<10} {'Streak':<8} {'Status':<10}")
        print("-"*80)
        
        for habit in habits:
            status = "✓ Active" if not habit.is_broken() else "✗ Broken"
            print(f"{habit.habit_id:<5} {habit.name:<25} {habit.periodicity:<10} "
                  f"{habit.get_current_streak():<8} {status:<10}")
        
        print("="*80)
        print(f"Total habits: {len(habits)}\n")
    
    def complete_habit(self):
        """Mark a habit as completed."""
        self.list_habits()
        
        try:
            habit_id = int(input("\nEnter habit ID to mark as complete: ").strip())
            habit = self.db.get_habit(habit_id)
            
            if not habit:
                print(f"❌ Habit with ID {habit_id} not found!")
                return
            
            # Check if already completed today/this week
            now = datetime.now()
            if habit.periodicity == 'daily':
                if any(c.date() == now.date() for c in habit.completions):
                    print(f"⚠️  Habit '{habit.name}' already completed today!")
                    return
            else:  # weekly
                week_start = now.date() - timedelta(days=now.weekday())
                week_end = week_start + timedelta(days=6)
                if any(week_start <= c.date() <= week_end for c in habit.completions):
                    print(f"⚠️  Habit '{habit.name}' already completed this week!")
                    return
            
            self.db.add_completion(habit_id)
            habit = self.db.get_habit(habit_id)  # Reload to get updated streak
            print(f"\n✅ Habit '{habit.name}' marked as complete!")
            print(f"🔥 Current streak: {habit.get_current_streak()} {habit.periodicity} period(s)")
            
        except ValueError:
            print("❌ Invalid input! Please enter a valid habit ID.")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def delete_habit(self):
        """Delete a habit."""
        self.list_habits()
        
        try:
            habit_id = int(input("\nEnter habit ID to delete: ").strip())
            habit = self.db.get_habit(habit_id)
            
            if not habit:
                print(f"❌ Habit with ID {habit_id} not found!")
                return
            
            confirm = input(f"⚠️  Are you sure you want to delete '{habit.name}'? (yes/no): ").strip().lower()
            
            if confirm == 'yes':
                self.db.delete_habit(habit_id)
                print(f"✅ Habit '{habit.name}' deleted successfully!")
            else:
                print("❌ Deletion cancelled.")
                
        except ValueError:
            print("❌ Invalid input! Please enter a valid habit ID.")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def update_habit(self):
        """Update habit details."""
        self.list_habits()
        
        try:
            habit_id = int(input("\nEnter habit ID to update: ").strip())
            habit = self.db.get_habit(habit_id)
            
            if not habit:
                print(f"❌ Habit with ID {habit_id} not found!")
                return
            
            print(f"\nUpdating habit: {habit.name}")
            new_name = input(f"New name (press Enter to keep '{habit.name}'): ").strip()
            
            if new_name:
                habit.name = new_name
            
            print("\nPeriodicity options:")
            print(f"  Current: {habit.periodicity}")
            print("  1. Daily")
            print("  2. Weekly")
            choice = input("Select new periodicity (or press Enter to keep current): ").strip()
            
            if choice:
                periodicity_map = {'1': 'daily', '2': 'weekly'}
                new_periodicity = periodicity_map.get(choice)
                if new_periodicity:
                    habit.periodicity = new_periodicity
            
            self.db.update_habit(habit)
            print(f"\n✅ Habit updated successfully!")
            
        except ValueError:
            print("❌ Invalid input! Please enter a valid habit ID.")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def analyze_habits(self):
        """Display analytics menu and handle analysis options."""
        print("\n📊 Habit Analytics")
        print("-" * 60)
        print("1. List all tracked habits")
        print("2. List habits by periodicity (daily/weekly)")
        print("3. Show longest streak across all habits")
        print("4. Show longest streak for specific habit")
        print("5. Show struggling habits (completion rate < 50%)")
        print("6. Show top performers")
        print("7. Back to main menu")
        
        choice = input("\nSelect option (1-7): ").strip()
        
        habits = self.db.get_all_habits()
        
        if choice == '1':
            habit_names = analytics.get_all_tracked_habits(habits)
            print(f"\n📋 All tracked habits ({len(habit_names)}):")
            for i, name in enumerate(habit_names, 1):
                print(f"  {i}. {name}")
        
        elif choice == '2':
            period = input("Enter periodicity (daily/weekly): ").strip().lower()
            filtered = analytics.filter_by_periodicity(habits, period)
            print(f"\n📋 {period.capitalize()} habits ({len(filtered)}):")
            for habit in filtered:
                print(f"  • {habit.name} - Streak: {habit.get_current_streak()}")
        
        elif choice == '3':
            longest = analytics.get_longest_streak_all_habits(habits)
            best_habit = analytics.get_habit_with_longest_streak(habits)
            print(f"\n🏆 Longest streak: {longest} period(s)")
            if best_habit:
                print(f"   Achieved by: {best_habit.name} ({best_habit.periodicity})")
        
        elif choice == '4':
            self.list_habits()
            try:
                habit_id = int(input("\nEnter habit ID: ").strip())
                habit = self.db.get_habit(habit_id)
                if habit:
                    longest = analytics.get_longest_streak_for_habit(habit)
                    print(f"\n🏆 Longest streak for '{habit.name}': {longest} {habit.periodicity} period(s)")
                else:
                    print("❌ Habit not found!")
            except ValueError:
                print("❌ Invalid habit ID!")
        
        elif choice == '5':
            struggling = analytics.get_struggling_habits(habits)
            print(f"\n⚠️  Struggling habits ({len(struggling)}):")
            for habit in struggling:
                rate = analytics.calculate_completion_rate(habit)
                print(f"  • {habit.name}: {rate:.1f}% completion rate (last 30 days)")
        
        elif choice == '6':
            sorted_habits = analytics.sort_habits_by_streak(habits)[:5]
            print(f"\n🌟 Top 5 performers:")
            for i, habit in enumerate(sorted_habits, 1):
                print(f"  {i}. {habit.name} - {habit.get_current_streak()} {habit.periodicity} streak")
        
        elif choice == '7':
            return
        
        else:
            print("❌ Invalid option!")
    
    def display_summary(self):
        """Display overall statistics summary."""
        habits = self.db.get_all_habits()
        summary = analytics.get_habits_summary(habits)
        
        print("\n📊 Overall Statistics")
        print("="*60)
        print(f"Total Habits:          {summary['total_habits']}")
        print(f"  • Daily habits:      {summary['daily_habits']}")
        print(f"  • Weekly habits:     {summary['weekly_habits']}")
        print(f"\nStatus:")
        print(f"  • Active habits:     {summary['active_habits']} ✓")
        print(f"  • Broken habits:     {summary['broken_habits']} ✗")
        print(f"\nPerformance:")
        print(f"  • Total completions: {summary['total_completions']}")
        print(f"  • Longest streak:    {summary['longest_streak']} period(s) 🏆")
        print(f"  • Average streak:    {summary['average_streak']} period(s)")
        print("="*60)
    
    def run(self):
        """Main CLI loop."""
        self.display_banner()
        
        while self.running:
            try:
                command = input("\n> ").strip().lower()
                
                if command == 'help':
                    self.display_help()
                elif command == 'create':
                    self.create_habit()
                elif command == 'list':
                    self.list_habits()
                elif command == 'complete':
                    self.complete_habit()
                elif command == 'delete':
                    self.delete_habit()
                elif command == 'update':
                    self.update_habit()
                elif command == 'analyze':
                    self.analyze_habits()
                elif command == 'summary':
                    self.display_summary()
                elif command == 'exit':
                    print("\n👋 Thank you for using Habit Tracker! Keep building great habits!")
                    self.running = False
                elif command == '':
                    continue
                else:
                    print(f"❌ Unknown command: '{command}'. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Exiting Habit Tracker. See you next time!")
                self.running = False
            except Exception as e:
                print(f"❌ An error occurred: {e}")
        
        self.db.close()


def main():
    """Entry point for the application."""
    cli = HabitTrackerCLI("habits.db")
    cli.run()


if __name__ == "__main__":
    main()
