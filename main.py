import os
import json

from exercises import *
from difflib import get_close_matches
from platformdirs import user_data_dir

folder = user_data_dir(appname="MyWorkoutApp", appauthor="MyName")
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

def log_PR(exercise, weight_input, reps_input, prs, valid_exercises):
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
        
    prs[exercise] = {"weight": weight, "reps": reps}
    return True, f"Your PR on {exercise.title()} is {weight}kg {reps:g}x reps!" 

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

def get_workout_logs_with_index(path):
    workouts_data = load_data(path)
    logs = workouts_data.get("logs", [])
    indexed = list(enumerate(logs))
    return list(reversed(indexed))


def delete_workout_log(path, index):
    workouts_data = load_data(path)
    logs = workouts_data.get("logs", [])
    if 0 <= index < len(logs):
        logs.pop(index)
    workouts_data["logs"] = logs
    save_data(path, workouts_data)
    return logs


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

def process_workout(workout, prs, valid_exercises, path_data, data):
    logged_prs = []

    for exercise in workout["exercises"]:
        exercise_name = exercise["name"].lower()
        sets = exercise["sets"]
        if not sets:
            continue

        is_new_exercise = exercise_name not in prs

        if is_new_exercise:
            best_set = max(sets, key=lambda s: s.get("total_weight") or s.get("weight", 0))
            weight = best_set.get("total_weight") or best_set.get("weight")
            reps = best_set.get("reps")
            success, msg = log_PR(exercise_name, str(weight), str(reps), prs, valid_exercises)
            logged_prs.append({"exercise": exercise_name, "success": success, "message": msg})
        else:
            for series in sets:
                has_pr_tag = any(tag["code"] == "PR" for tag in series["tags"])
                if has_pr_tag:
                    weight = series.get("total_weight") or series.get("weight")
                    reps = series.get("reps")
                    success, msg = log_PR(exercise_name, str(weight), str(reps), prs, valid_exercises)
                    logged_prs.append({"exercise": exercise_name, "success": success, "message": msg})

    if logged_prs:
        data["prs"] = prs
        save_data(path_data, data)

    return logged_prs