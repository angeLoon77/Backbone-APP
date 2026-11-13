import json
import os
import re
import requests
from platformdirs import user_data_dir
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")
TIMEOUT = 45

_token = None
_exercise_ids = {}
_exercise_cache = None


class ApiError(Exception):
    """Network error or unexpected API response."""


class SessionExpired(ApiError):
    """Missing or expired token. The user should log in again."""

def get_exercises():
    global _exercise_cache
    if _exercise_cache is None:
        _exercise_cache = _fetch_exercises()
    return _exercise_cache

# BASE/TOKENS

def set_token(token):
    global _token, _exercise_cache
    _token = token
    _exercise_cache = None
    _exercise_ids.clear()


def get_token():
    return _token


def has_token():
    return _token is not None


def _session_dirs():
    folders = []
    app_data = os.environ.get("FLET_APP_STORAGE_DATA")
    if app_data:
        folders.append(app_data)
    folders.append(user_data_dir(appname="BackBone", appauthor="angeLoon DEV"))
    unique = []
    for folder in folders:
        if folder and folder not in unique:
            unique.append(folder)
    return unique


def load_saved_token():
    for folder in _session_dirs():
        path = os.path.join(folder, "session.json")
        try:
            with open(path, encoding="utf-8") as f:
                token = json.load(f).get("token")
        except (OSError, ValueError):
            continue
        if isinstance(token, str) and token:
            return token
    return None


def remember_session():
    if not _token:
        return
    payload = json.dumps({"token": _token})
    for folder in _session_dirs():
        try:
            os.makedirs(folder, exist_ok=True)
            with open(os.path.join(folder, "session.json"), "w", encoding="utf-8") as f:
                f.write(payload)
        except OSError:
            continue


def forget_session():
    set_token(None)
    for folder in _session_dirs():
        path = os.path.join(folder, "session.json")
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError:
            continue


def _request(method, path, **kwargs):
    headers = {}
    if _token:
        headers["Authorization"] = f"Bearer {_token}"
    try:
        return requests.request(
            method, f"{API_URL}{path}", headers=headers, timeout=TIMEOUT, **kwargs
        )
    except requests.RequestException:
        raise ApiError("Could not reach the server")


def _error_message(response):
    try:
        return response.json().get("error", "Unexpected error")
    except ValueError:
        return "Unexpected error"


def _check(response, ok_codes):
    if response.status_code in ok_codes:
        return
    if response.status_code == 401:
        set_token(None)
        raise SessionExpired("Session expired, please log in again")
    if response.status_code == 400:
        raise ValueError(_error_message(response))
    raise ApiError(_error_message(response))


def _to_iso(date):
    """Backbone API accepts dates in YYYY-MM-DD format"""
    if hasattr(date, "isoformat"):
        return date.isoformat()
    if isinstance(date, str):
        m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", date.strip())
        if m:
            day, month, year = m.groups()
            return f"{year}-{int(month):02d}-{int(day):02d}"
    return date

# USERS

def register(username, password):
    r = _request("POST", "/register", json={"username": username, "password": password})
    if r.status_code == 201:
        return r.json()["user_id"]
    if r.status_code in (400, 409):
        raise ValueError(_error_message(r))
    raise ApiError(_error_message(r))


def login(username, password):
    r = _request("POST", "/login", json={"username": username, "password": password})
    if r.status_code == 200:
        set_token(r.json()["token"])
        return True
    if r.status_code == 401:
        return False
    raise ApiError(_error_message(r))


def init_db():
    pass 

def _fetch_exercises():
    r = _request("GET", "/exercises")
    _check(r, (200,))
    data = r.json()
    _exercise_ids.clear()
    _exercise_ids.update({ex["name"].lower(): ex["id"] for ex in data})
    return [(ex["name"].lower(), ex["muscle_group"]) for ex in data]


def get_exercise_id(name):
    if not _exercise_ids:
        get_exercises()
    return _exercise_ids.get(name.lower())


def get_exercises_by_muscle_group(group):
    return [name for name, muscle_group in get_exercises() if muscle_group == group]

def get_prs_by_muscle_group(user_id, muscle_group):
    r = _request("GET", f"/prs/group/{quote(muscle_group)}")
    _check(r, (200,))
    return [(p["name"].lower(), p["weight"], p["reps"], p["date"]) for p in r.json()]

def delete_prs_by_exercise(user_id, exercise_id):
    r = _request("DELETE", f"/exercises/{int(exercise_id)}/prs")
    _check(r, (200,))
    return r.json()["deleted"]


def add_pr(user_id, exercise_id, weight, reps, date):
    r = _request(
        "POST",
        "/prs",
        json={
            "exercise_id": int(exercise_id),
            "weight": float(weight),
            "reps": int(reps),
            "date": _to_iso(date),
        },
    )
    _check(r, (201,))
    return r.json()["pr_id"]


def get_prs(user_id):
    r = _request("GET", "/prs")
    _check(r, (200,))
    return r.json()