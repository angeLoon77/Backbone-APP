import os
import json

from exercises import *

folder = os.path.dirname(os.path.abspath(__file__))
path_data = os.path.join(folder, "data.json")

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
        reps = int(reps_input)
    except ValueError:
        return False, "Invalid Numeric Value"
    if weight < 0 or reps < 0:
        return False, "Value must be 1 or More"
        
    prs[exercise] = {"weight": weight, "reps": reps}
    return True, f"Your PR on {exercise.title()} is {weight_input}kg {reps_input}x reps!" 

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
