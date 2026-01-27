# Habit Tracker Application

A Python-based command-line habit tracking application that helps users build and maintain positive habits through consistent tracking and insightful analytics.

**Course:** Object Oriented and Functional Programming with Python (DLBDSOOFPP01)  
**Institution:** IU International University of Applied Sciences

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Design Philosophy](#design-philosophy)
- [Testing](#testing)
- [Requirements](#requirements)

## 🎯 Overview

This habit tracker application allows users to:
- Create and manage daily and weekly habits
- Track habit completions over time
- Analyze streaks and performance metrics
- Identify struggling habits and celebrate successes

The project demonstrates the integration of **Object-Oriented Programming (OOP)** and **Functional Programming (FP)** principles in Python.

## ✨ Features

### Core Functionality
- **Create Habits**: Define new daily or weekly habits
- **Track Completions**: Mark habits as completed with timestamp recording
- **View Progress**: See current status and streaks for all habits
- **Update Habits**: Modify habit names and periodicity
- **Delete Habits**: Remove habits you no longer want to track

### Analytics (Functional Programming)
- List all tracked habits
- Filter habits by periodicity (daily/weekly)
- Calculate longest streaks across all habits
- Identify struggling habits (< 50% completion rate)
- View top performers sorted by current streak
- Generate comprehensive statistics summary

### Data Persistence
- SQLite database for reliable data storage
- Automatic creation of database schema
- Efficient querying with indexed tables
- Data integrity through foreign key constraints

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Setup Steps

1. **Clone or download the repository**
   ```bash
   git clone <your-github-repo-url>
   cd habit-tracker
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database with sample data**
   ```bash
   python seed_database.py
   ```
   
   This creates 5 predefined habits with 4 weeks of sample tracking data:
   - 3 daily habits (Morning Exercise, Read for 30 minutes, Drink 8 glasses of water)
   - 2 weekly habits (Grocery Shopping, Review Weekly Goals)

4. **Run the application**
   ```bash
   python main.py
   ```

## 💻 Usage

### Starting the Application

Run the main script:
```bash
python main.py
```

You'll see the welcome banner and command prompt:
```
============================================================
          🎯 HABIT TRACKER - Build Better Habits 🎯
============================================================
Type 'help' to see available commands

>
```

### Available Commands

| Command    | Description                                    |
|------------|------------------------------------------------|
| `create`   | Create a new habit                             |
| `list`     | Display all habits with current status         |
| `complete` | Mark a habit as completed                      |
| `update`   | Modify habit name or periodicity               |
| `delete`   | Remove a habit permanently                     |
| `analyze`  | Access analytics menu for detailed insights    |
| `summary`  | View overall statistics dashboard              |
| `help`     | Display help menu                              |
| `exit`     | Quit the application                           |

### Example Workflow

1. **View your habits**
   ```
   > list
   ```

2. **Mark a habit as complete**
   ```
   > complete
   Enter habit ID to mark as complete: 1
   ✅ Habit 'Morning Exercise' marked as complete!
   🔥 Current streak: 5 daily period(s)
   ```

3. **Analyze your progress**
   ```
   > analyze
   Select option: 3
   🏆 Longest streak: 14 period(s)
      Achieved by: Read for 30 minutes (daily)
   ```

4. **View summary statistics**
   ```
   > summary
   
   📊 Overall Statistics
   ============================================================
   Total Habits:          5
     • Daily habits:      3
     • Weekly habits:     2
   
   Status:
     • Active habits:     4 ✓
     • Broken habits:     1 ✗
   
   Performance:
     • Total completions: 87
     • Longest streak:    14 period(s) 🏆
     • Average streak:    6.2 period(s)
   ```

## 📁 Project Structure

```
OOFPP_Habits_Tracker/
├── src/
│   ├── data/
│   │   └── seed_database.py    # Script to create sample data
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── habit.py            # Habit class (OOP implementation)
│   │   ├── database.py         # SQLite database manager
│   │   └── analytics.py        # Analytics module (FP implementation)
│   └── main.py                 # CLI interface and main entry point
├── tests/
│   └── test_habits.py          # Unit tests (pytest)
├── pyproject.toml              # Project configuration
├── requirements.txt            # Python dependencies
├── uv.lock                     # Dependency lock file
├── habits.db                   # SQLite database (created on first run)
└── README.md                   # This file
```

## 🏗️ Design Philosophy

### Object-Oriented Programming (OOP)

The **Habit** class encapsulates all habit-related data and behavior:
- **Attributes**: name, periodicity, created_at, completions
- **Methods**: add_completion(), get_current_streak(), get_longest_streak(), is_broken()
- **Encapsulation**: Internal state management with public interface

The **DatabaseManager** class handles all persistence operations:
- Separation of concerns (data access layer)
- Single Responsibility Principle
- Clean API for CRUD operations

### Functional Programming (FP)

The **analytics** module uses functional programming principles:
- **Pure functions**: No side effects, deterministic outputs
- **Higher-order functions**: Functions that operate on other functions
- **Immutability**: Original data is never modified
- **Composition**: Complex operations built from simple functions

Example FP patterns used:
```python
# map, filter, reduce
habit_names = map(lambda h: h.name, habits)
daily_habits = filter(lambda h: h.periodicity == 'daily', habits)
total_completions = reduce(lambda a, b: a + len(b.completions), habits, 0)

# Function composition
get_top_daily_habits = compose(sort_by_streak, filter_daily)
```

### Database Design

**habits** table:
- id (PRIMARY KEY)
- name (TEXT)
- periodicity (TEXT)
- created_at (TEXT/ISO format)

**completions** table:
- id (PRIMARY KEY)
- habit_id (FOREIGN KEY → habits.id)
- completed_at (TEXT/ISO format)

Benefits:
- Normalized structure prevents data duplication
- Foreign keys maintain referential integrity
- Indexes enable fast querying
- Timestamps stored in ISO format for timezone handling

## 🧪 Testing

The project includes comprehensive unit tests using **pytest**.

### Running Tests

```bash
# Run all tests with verbose output
pytest test_habits.py -v

# Run with coverage report
pytest test_habits.py --cov=. --cov-report=html

# Run specific test class
pytest test_habits.py::TestHabitClass -v
```

### Test Coverage

The test suite covers:
- ✅ Habit class methods (creation, streaks, completion tracking)
- ✅ Database operations (CRUD, completions, filtering)
- ✅ Analytics functions (all FP functions)
- ✅ Edge cases (broken streaks, invalid inputs, empty data)

Example test output:
```
test_habits.py::TestHabitClass::test_habit_creation PASSED
test_habits.py::TestHabitClass::test_current_streak_calculation PASSED
test_habits.py::TestDatabaseManager::test_save_and_retrieve_habit PASSED
test_habits.py::TestAnalytics::test_longest_streak_all_habits PASSED
...
======================== 28 passed in 0.45s ========================
```

## 📦 Requirements

Create a `requirements.txt` file with:

```
pytest>=7.0.0
```

That's it! The application uses only Python standard library for core functionality, with pytest for testing.

## 🔧 Technical Specifications

- **Python Version**: 3.7+
- **Database**: SQLite3 (built-in)
- **Testing Framework**: pytest
- **External Dependencies**: None (for core app)

## 📈 Future Enhancements

Potential improvements for future versions:
- 📱 GUI using tkinter or web interface with Flask
- ☁️ Cloud synchronization
- 📊 Data visualization (graphs and charts)
- 🔔 Reminder notifications
- 📤 Export data to CSV/JSON
- 🎯 Goal setting and milestone tracking
- 📱 Mobile app integration

## 🤝 Contributing

This is an academic project for the IU course DLBDSOOFPP01. However, feedback and suggestions are welcome!

## 📄 License

This project is created for educational purposes as part of the IU International University coursework.

## 👤 Author

**Happiness Oribhunuebho**  
Student ID: 92133053
Course: DLBDSOOFPP01 - Object Oriented and Functional Programming with Python  
Institution: IU International University of Applied Sciences

---

## 🆘 Troubleshooting

### Database Issues
- If you encounter database errors, delete `habits.db` and run `seed_database.py` again
- Ensure you have write permissions in the application directory

### Import Errors
- Make sure all Python files are in the same directory
- Verify Python 3.7+ is installed: `python --version`

### Test Failures
- Ensure no `test_habits.db` file exists before running tests
- Run tests from the project root directory
