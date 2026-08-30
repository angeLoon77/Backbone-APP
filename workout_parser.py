import re
from datetime import date

if __name__ == "__main__":
    text = ("""""")

def parse_header(text):
    pattern = r"(?:(\d{1,2})/(\d{1,2})\s*-\s*)?(.+)"
    result = re.match(pattern, text.strip())

    if not result:
        return None

    day, month, title = result.groups()
    year = date.today().year

    if day is None:
        full_date = date.today().strftime("%d/%m/%Y")
    else:
        full_date = f"{int(day):02d}/{int(month):02d}/{year}"

    return {"date": full_date, "title": title}

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
            "weight": int(weight),
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
    pattern = r"^(sem\s+)?cardio\s*:?\s*(.*)$"
    result = re.match(pattern, text, re.IGNORECASE)

    if not result:
        return None
    
    sem_prefix, detail = result.groups()
    done = sem_prefix is None
    detail = detail.strip() if detail else None

    return {"done": done, "detail": detail}

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

    return {
        "date": header["date"],
        "title": header["title"],
        "exercises": exercises,
        "cardio": cardio,
    }

    print(parse_workout(text))