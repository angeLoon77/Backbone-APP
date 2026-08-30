import re
from datetime import date

text = ("close row - M", "lat pulldown wide")

def parse_header(text):
    pattern = r"(?:(\d{1,2}/\d{1,2})\s*-\s*)?(.+)"
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

    name, equipment = result.groups()
    return {"name": name.strip(), "equipment": equipment}

def parse_set_line(text):
    pattern = r"(\d+(?:\.\d+)?)x\s*(\d+)kg(?:\s*-\s*(.+))?$"
    result = re.match(pattern, text.strip())

    if not result:
        return None

    reps, weight, tags_str = result.groups()

    tags = []
    if tags_str:
        tags = [t.strip() for t in tags_str.split(",")]

    return {"reps": float(reps), "weight": int(weight), "tags": tags}

print(parse_set_line("10x 40kg(80kg)"))
print(parse_set_line("6x 60kg - F, +1"))