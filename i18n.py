import json
from pathlib import Path

_translations: dict = {}
_reverse_exercises: dict[str, str] = {}
_current_lang: str = "en"

BASE_DIR = Path(__file__).resolve().parent


# Load translations from a JSON file based on the provided language code.
# If the specified language file does not exist, default to English ("en.json").
def load_language(lang: str) -> None:
    global _translations, _reverse_exercises, _current_lang
    lang = (lang or "en").strip().lower()
    file_path = BASE_DIR / "locales" / f"{lang}.json"
    if not file_path.exists():
        lang = "en"
        file_path = BASE_DIR / "locales" / "en.json"

    with open(file_path, "r", encoding="utf-8") as f:
        _translations = json.load(f)

    _current_lang = lang
    exercises = _translations.get("exercises", {})
    _reverse_exercises = {}
    for db_key, translated_name in exercises.items():
        _reverse_exercises[db_key.strip().lower()] = db_key.lower()
        _reverse_exercises[translated_name.strip().lower()] = db_key.lower()


def get_current_language() -> str:
    return _current_lang


# Translate UI strings and interpolate dynamic placeholders like {count} or {exercise}.
def t(key: str, **kwargs) -> str:
    text = _translations.get("ui", {}).get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except KeyError:
            return text
    return text


# Translate a database exercise name for UI display.
def t_ex(db_name: str) -> str:
    if not db_name:
        return ""
    return _translations.get("exercises", {}).get(db_name.lower(), db_name.title())


# Translate a database muscle group for UI display.
def t_group(db_group: str) -> str:
    if not db_group:
        return ""
    fallback = str(db_group).replace("_", " ").title()
    return _translations.get("muscle_groups", {}).get(db_group.lower(), fallback)


# Convert raw user input (in any loaded language) back to the lowercase English DB key.
def resolve_exercise_name(raw_input: str) -> str:
    cleaned = raw_input.strip().lower()
    return _reverse_exercises.get(cleaned, cleaned)

load_language("en")