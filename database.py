import sqlite3
from pathlib import Path

base_dir = Path(__file__).resolve().parent
db_path = base_dir / "database.db"

VALID_TABLES = ["exercises", "prs"]

def get_connection():
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def create_exercise_table():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS exercises 
        (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT NOT NULL UNIQUE, 
        muscle_group TEXT NOT NULL
        )
        """)
    conn.commit()
    conn.close()

def create_prs_table():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS prs
        (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL, 
        exercise_id INTEGER NOT NULL, 
        weight REAL NOT NULL, 
        reps INTEGER NOT NULL, 
        date TEXT NOT NULL,
        FOREIGN KEY (exercise_id) REFERENCES exercises (id) ON DELETE CASCADE
        )
        """)
    conn.commit()
    conn.close()

def add_exercise(name, muscle_group):
    conn = get_connection()
    conn.execute(
        "INSERT OR IGNORE INTO exercises (name, muscle_group) VALUES (?, ?)",
        (name.title(), muscle_group),
    )
    conn.commit()
    conn.close()

def add_pr(user_id, exercise_id, weight, reps, date):
    conn = get_connection()
    conn.execute(
        "INSERT INTO prs (user_id, exercise_id, weight, reps, date) VALUES (?, ?, ?, ?, ?)",
        (user_id, exercise_id, weight, reps, date),
    )
    conn.commit()
    conn.close()

def get_prs_by_muscle_group(user_id, muscle_group):
    conn = get_connection()
    cursor = conn.execute(""" 
    SELECT exercises.name, prs.weight, prs.reps, prs.date FROM prs JOIN exercises ON prs.exercise_id = exercises.id
    WHERE prs.user_id = ? AND exercises.muscle_group = ?""", (user_id, muscle_group))
    prs = cursor.fetchall()
    conn.close()
    return prs

def get_exercises():
    conn = get_connection()
    cursor = conn.execute("SELECT name, muscle_group FROM exercises")
    exercises = cursor.fetchall()
    conn.close()
    return exercises

def get_exercises_by_muscle_group(group):
    exercises = get_exercises()
    result = []
    for ex in exercises:
        if ex[1] == group:
            result.append(ex[0])
    return result

def drop_table(table_name):
    conn = get_connection()
    if table_name not in VALID_TABLES:
        raise ValueError(f"Invalid table name:{table_name}")
    conn.execute(f"DROP TABLE IF EXISTS {table_name}")
    conn.commit()
    conn.close()

EXERCISES = [
    # chest
    ("Bench Press", "chest"),
    ("Bench Press Smith Machine", "chest"),
    ("Dumbbell Press", "chest"),
    ("Incline Press", "chest"),
    ("Smith Incline Press", "chest"),
    ("Dumbbell Incline Press", "chest"),
    ("Pec Deck", "chest"),
    ("High To Low", "chest"),
    ("Low To High", "chest"),
    # legs
    ("Leg Press", "legs"),
    ("Deadlift", "back"),
    ("Squat", "legs"),
    ("Seated Leg Curl", "legs"),
    ("Leg Extension", "legs"),
    ("Hip Adduction", "legs"),
    # glutes
    ("Hip Thrust", "glutes"),
    ("Glute Bridge", "glutes"),
    ("Hip Abduction", "glutes"),
    # calves
    ("Calf Raise", "calves"),
    ("Seated Calf Raise", "calves"),
    ("Standing Calf Raise", "calves"),
    # shoulders
    ("Shoulder Press", "shoulders"),
    ("Lateral Raise", "shoulders"),
    ("Front Raise", "shoulders"),
    # back
    ("Lat Pulldown Wide", "back"),
    ("Lat Pulldown Close", "back"),
    ("T-Bar Row", "back"),
    ("Seated Row", "back"),
    ("Bent Over Row", "back"),
    ("One Arm Row", "back"),
    ("Pullover", "back"),
    # biceps
    ("Barbell Curl", "biceps"),
    ("Dumbbell Curl", "biceps"),
    ("Hammer Curl", "biceps"),
    # triceps
    ("Triceps Pushdown", "triceps"),
    ("Triceps Pulley", "triceps"),
    ("Skull Crusher", "triceps"),
    ("Bench Dips", "triceps"),
    ("Overhead Triceps Extension", "triceps"),
    ("Dumbbell Overhead Triceps Extension", "triceps"),
    ("Triceps Extension", "triceps"),
    # forearms / core
    ("Wrist Curl", "forearms"),
    ("Cable Crunch", "core"),
]

if __name__ == "__main__":
    add_pr(1, 10, 200, 12, "2026-10-15")
    print(get_prs_by_muscle_group(1, "chest"))