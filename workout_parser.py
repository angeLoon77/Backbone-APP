import re
from datetime import date

def parse_header(text):
    text = text.strip()
    date_pattern = r"^(\d{1,2})/(\d{1,2})(?:\s*-\s*(.+))?$"
    match = re.match(date_pattern, text)
    year = date.today().year

    if match:
        day, month, title = match.groups()
        full_date = f"{int(day):02d}/{int(month):02d}/{year}"
        return {"date": full_date, "title": title}
    else:
        full_date = date.today().strftime("%d/%m/%Y")
        return {"date": full_date, "title": text}

def parse_exercise_line(text):
    pattern = r"(.+?)(?:\s*-\s*([A-Z]))?$"
    result = re.match(pattern, text.strip())

    if not result:
        return None

    name, suffix = result.groups() 
    equipment = None
    if suffix:
        suffix = suffix.strip()
        if re.match(r"^[A-Z]$", suffix):
            equipment = suffix
    return {"name": name.strip(), "equipment": equipment}

def parse_tag(tag_str):
    tag_str = tag_str.strip()

    m = re.match(r"^(\d+)\s*RIR$", tag_str, re.IGNORECASE)
    if m:
        return {"code": "RIR", "value": int(m.group(1)), "note": None}

    m = re.match(r"^\+(\d+)(?:\s+(.+))?$", tag_str)
    if m:
        return {"code": "+N", "value": int(m.group(1)), "note": m.group(2)}

    m = re.match(r"^(F|PR|W)\s*\(?(.*?)\)?$", tag_str)
    if m:
        code, note = m.groups()
        return {"code": code, "value": None, "note": note.strip() if note else None}

    return {"code": None, "value": None, "note": tag_str}


def parse_series_line(text):
    text = text.strip()

    bilateral_pattern = r"(\d+(?:\.\d+)?)x\s*esq\s*/\s*(\d+(?:\.\d+)?)x\s*dir\s*(\d+(?:\.\d+)?)kg(?:\s*-\s*(.+))?$"
    bilateral_result = re.match(bilateral_pattern, text)
    if bilateral_result:
        left_reps, right_reps, weight, tags_str = bilateral_result.groups()
        tags = [parse_tag(t) for t in tags_str.split(",")] if tags_str else []
        return {
            "reps_left": float(left_reps),
            "reps_right": float(right_reps),
            "weight": float(weight),
            "total_weight": None,
            "note": None,
            "tags": tags,
        }

    pattern = r"(\d+(?:\.\d+)?)x\s*(\d+(?:\.\d+)?)kg(?:\s*\(([^)]+)\))?(?:\s*-\s*(.+))?$"
    result = re.match(pattern, text)
    if not result:
        return None

    reps, weight, paren_content, tags_str = result.groups()
    tags = [parse_tag(t) for t in tags_str.split(",")] if tags_str else []

    total_weight = None
    note = None
    if paren_content:
        paren_match = re.match(r"^(\d+)kg$", paren_content.strip())
        if paren_match:
            total_weight = int(paren_match.group(1))
        else:
            note = paren_content.strip()

    return {
        "reps": float(reps),
        "weight": float(weight),
        "total_weight": total_weight,
        "note": note,
        "tags": tags,
    }

def parse_cardio_line(text):
    text = text.strip()
    match = re.search(r"(?:(sem)\s+)?\bcardio\b", text, re.IGNORECASE)

    if not match:
        return None

    done = match.group(1) is None

    duration_match = re.search(r"(\d+(?:\.\d+)?)\s*m(?:in)?\b", text, re.IGNORECASE)
    distance_match = re.search(r"(\d+(?:\.\d+)?)\s*km\b", text, re.IGNORECASE)

    duration_min = float(duration_match.group(1)) if duration_match else None
    distance_km = float(distance_match.group(1)) if distance_match else None

    return { 
        "done": done,
        "duration_min": duration_min,
        "distance_km": distance_km,
        "raw": text,
    }

def parse_workout(text):
    lines = [line for line in text.strip().split("\n") if line.strip()]

    header = parse_header(lines[0])
    if header is None:
        raise ValueError

    exercises = []
    current_exercise = None
    cardio = None

    for line in lines[1:]:
        cardio_result = parse_cardio_line(line)
        if cardio_result:
            cardio = cardio_result
            continue

        sets = parse_series_line(line)
        if sets:
            if current_exercise:
                current_exercise["sets"].append(sets)
        else:
            exercise_info = parse_exercise_line(line)
            if exercise_info is None:
                raise ValueError(f"The Line Couldn't be interpreted: {line!r}")
            current_exercise = {
                "name": exercise_info["name"],
                "equipment": exercise_info["equipment"],
                "sets": [],
            }
            exercises.append(current_exercise)   

    total_sets = sum(len(ex["sets"]) for ex in exercises)
    if not exercises or total_sets == 0:
        raise ValueError

    return {
        "date": header["date"],
        "title": header["title"],
        "exercises": exercises,
        "cardio": cardio,
    }

# Talvez seja nescessário remover esse parser abaixo,  ele não é tanto pra progressão de carga, mas sim pra registrar o treino feito

def parse_alt_workout(text):
    lines = [line.strip() for line in text.strip().split("\n") if line.strip()]

    exercises = []
    current_exercise = None
    current_weight = None

    exercise_pattern = re.compile(r"^(.+?)\s*\d+\s*[×xX]\s*\d+(?:[\u2013-]\d+)?\s*-\s*(\d+(?:\.\d+)?)kg$")
    series_pattern = re.compile(r"^\d+\s*s[ée]rie\s*(\d+)\s*repeti[çc][õo]es?$", re.IGNORECASE)

    for line in lines:
        ex_match = exercise_pattern.match(line)
        if ex_match:
            name, weight = ex_match.groups()
            current_weight = float(weight)
            current_exercise = {"name": name.strip(), "equipment": None, "sets": []}
            exercises.append(current_exercise)
            continue

        series_match = series_pattern.match(line)
        if series_match and current_exercise:
            reps = float(series_match.group(1))
            current_exercise["sets"].append({
                "reps": reps,
                "weight": current_weight,
                "total_weight": None,
                "note": None,
                "tags": [],
            })
            continue

    # Check if any exercises were found and if they contain sets

    total_sets = sum(len(ex["sets"]) for ex in exercises)
    if not exercises or total_sets == 0:
        raise ValueError("No Exercise Found or No Sets Found in the Workout!")

    return {
        "date": date.today().strftime("%d/%m/%Y"),
        "title": None,
        "exercises": exercises,
        "cardio": None,
    }
KNOWN_PARSERS = [parse_workout, parse_alt_workout]


def parse_any_workout(text):
    errors = []
    for parser in KNOWN_PARSERS:
        try:
            return parser(text)
        except Exception as e:
            errors.append(str(e))
    raise ValueError(f"No parser succeeded: {errors}")

if __name__ == "__main__":
    text = ("""""")