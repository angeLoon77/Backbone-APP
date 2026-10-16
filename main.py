import os
import json

import database as db
import datetime
from exercises import *
from difflib import get_close_matches
from platformdirs import user_data_dir

folder = user_data_dir(appname="BackBone", appauthor="angeLoon DEV")
os.makedirs(folder, exist_ok=True)
path_data = os.path.join(folder, "data.json")
path_workouts = os.path.join(folder, "workouts.json")

def load_data(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_data(path, data):
    with open (path, "w") as f:
        json.dump(data, f, indent=4)

# Function to log a personal record (PR) for a specific exercise, validating the input and updating the PRs dictionary

def log_PR(exercise, weight_input, reps_input, prs, valid_exercises, date=None):
    valid_exercises_lower = [ex.lower() for ex in valid_exercises]
    if exercise not in valid_exercises_lower:
        return False, f"{exercise} does not exist"

    try:
        weight = float(weight_input)
        reps = float(reps_input)
    except ValueError:
        return False, "Invalid Numeric Value"
    if weight < 0 or reps < 0:
        return False, "Value must be 1 or More"

    if reps > 99:
        return False, "Reps must be 2 digits or less"

    exercise_id = db.get_exercise_id(exercise)
    if exercise_id is None:
        return False, f"{exercise} does not exist"

    if date is None:
        date = datetime.date.today().isoformat()

    db.add_pr(1, exercise_id, weight, reps, date)

    prs.clear()
    prs.update(db.get_prs(1))

    return True, f"Your PR on {exercise.title()} is {weight}kg {reps:g}x reps!" 

# Function to delete a PR entry for a specific exercise from the data and save the updated data back to the file

def delete_pr(exercise_name,prs):
    exercise_id = db.get_exercise_id(exercise_name)
    if exercise_id is not None:
        db.delete_prs_by_exercise(1, exercise_id)
    prs.clear()
    prs.update(db.get_prs(1))
    return prs

# Function to log a workout entry, ensuring no duplicates based on raw text

def log_workout(path, workout, raw_text):
    workouts_data = load_data(path)
    logs = workouts_data.get("logs", [])

    if any(log["raw_text"] == raw_text for log in logs):
        return logs

    logs.append({
        "date": workout["date"],
        "title": workout["title"],
        "raw_text": raw_text,
        "cardio": workout.get("cardio"),
    })
    workouts_data["logs"] = logs
    save_data(path, workouts_data)
    return logs

# talvez deletar o get_workout_logs e usar so o get_workout_logs_with_index, mas por enquanto vou deixar os dois

def get_workout_logs(path):
    workouts_data = load_data(path)
    logs = workouts_data.get("logs", [])
    return list(reversed(logs))

# Function to get workout logs with their index in the list, useful for editing or deleting specific entries

def get_workout_logs_with_index(path):
    workouts_data = load_data(path)
    logs = workouts_data.get("logs", [])
    indexed = list(enumerate(logs))
    return list(reversed(indexed))

# Function to delete a workout log entry by index

def delete_workout_log(path, index):
    workouts_data = load_data(path)
    logs = workouts_data.get("logs", [])
    if 0 <= index < len(logs):
        logs.pop(index)
    workouts_data["logs"] = logs
    save_data(path, workouts_data)
    return logs

# Function to edit a workout log entry, updating its raw text and associated workout data

def edit_workout_log(path, index, new_raw_text, workout):
    workouts_data = load_data(path)
    logs = workouts_data.get("logs", [])
    if 0 <= index < len(logs):
        logs[index]["raw_text"] = new_raw_text
        logs[index]["date"] = workout["date"]
        logs[index]["title"] = workout["title"]
        logs[index]["cardio"] = workout.get("cardio")
    workouts_data["logs"] = logs
    save_data(path, workouts_data)
    return logs

# Function to calculate the next goal based on current PRs (I NEED TO IMPROVE THIS FUNCTION, IT'S NOT PERFECT, BUT IT'S A START)

def next_goal_calculation(prs):
    next_goal = {}

    for exercise, data in prs.items():
        current_weight = data["weight"]
        current_reps = data["reps"]

        if current_reps >=10:
            goal_weight = current_weight + 5
            goal_reps = 8
        else:
            goal_weight = current_weight
            goal_reps = current_reps + 1

        next_goal[exercise] =  {"weight": goal_weight, "reps": goal_reps}

    return next_goal

# Function to determine if a new set beats the current personal record (PR) for a given exercise

def beats_current_pr(prs, exercise_name, weight, reps):
    current = prs.get(exercise_name)
    if not current:
        return True
    if weight != current["weight"]:
        return weight > current["weight"]
    return reps > current["reps"]

def to_iso_date(date_text):
    try:
        return datetime.datetime.strptime(date_text, "%d/%m/%Y").date().isoformat()
    except (ValueError, TypeError):
        return None

# Registers a PR when the best valid set of an exercise beats the stored one
def process_workout(workout, prs, valid_exercises):
    logged_prs = []
    date = to_iso_date(workout.get("date"))

    for exercise in workout["exercises"]:
        exercise_name = exercise["name"].lower()
        sets = exercise["sets"]
        if not sets:
            continue

        eligible = [
            s for s in sets
            if s.get("reps") is not None
            and not any(tag["code"] == "W" for tag in s["tags"])
        ]
        if not eligible:
            continue

        best_set = max(eligible, key=lambda s: (s.get("total_weight") or s.get("weight", 0), s["reps"]))
        weight = best_set.get("total_weight") or best_set.get("weight")
        reps = best_set["reps"]

        if beats_current_pr(prs, exercise_name, weight, reps):
            success, msg = log_PR(exercise_name, str(weight), str(reps), prs, valid_exercises, date)
            logged_prs.append({"exercise": exercise_name, "success": success, "message": msg})

    return logged_prs