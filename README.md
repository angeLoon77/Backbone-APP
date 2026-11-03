<p align="center">
  <img src="assets/icon.png" width="120" alt="Backbone icon" />
</p>

<h1 align="center">Backbone</h1>

<p align="center">
  A workout tracker for Android and desktop where you just paste your training log and the app does the rest.
</p>

> 🚧 **Status:** in development (v1.14.1a). Built solo with Python and Flet.

## Why I built it

I already log my workouts as plain text in my notes, but it was tiring to figure out my next objective for each exercise on the day. Backbone reads that text directly: you paste the workout, and it extracts the exercises, sets, reps and weights, detects personal records, and keeps everything organized.

## Screenshots

<p align="center">
  <img src="images/prs.png" height="400" alt="Your PRs" />
  <img src="images/paste.png" height="400" alt="Paste Workout" />
  <img src="images/objectives.png" height="400" alt="Next Objectives" />
</p>

## Features

- **Paste Workout:** write a workout in free text and the parser extracts exercises, sets, reps and weights
- **Your PRs:** a personal record for each exercise, detected automatically from your logs
- **Log PR:** add a PR manually
- **Next Objectives:** the next target for each exercise, based on your current PR
- **History:** every logged workout with date and title, expandable and editable
- **Languages:** interface available in Portuguese and English
- **Online accounts and storage (in progress):** the online backend (accounts, PRs and exercises on PostgreSQL, behind a token-protected API) is built and tested. The app still runs on local SQLite until it is switched to the API client

## Workout format

```text
08/28 - your title
bench press
10x 40kg
8x 60kg - F, PR (notes)
```

The first line holds the date and an optional title. Then comes the exercise name, followed by one line per set (`reps x weight`). Tags after the set (`F` for failure, `PR` for personal record) and notes in parentheses are optional.

## How the online part works

```text
Backbone app (Flet)  →  Backbone API (Flask)  →  PostgreSQL (Neon)
```

The app never talks to the database directly. A database connection string bundled into an Android app could be extracted by anyone, so only the API holds the credentials. The app logs in through the API, receives a signed token, and sends it with each request. The API reads the user from the token, so a user can only see and change their own data.

The backend lives in its own repository, **`backbone-api`**, which also has the setup instructions (database, `.env` and running the server).

## Tech stack

- **Python**
- **Flet** (UI, Android and desktop)
- **SQLite3** (local database, used by the app today)
- **requests** (HTTP client used by the app to talk to the API)
- **Flask**, **PostgreSQL / Neon**, **psycopg2**, **bcrypt** (online backend, in `backbone-api`)

## Project structure

| File | Purpose |
|---|---|
| `main.py` | App entry point: UI screens and navigation |
| `core.py` | Core app logic: processing workouts, logging PRs and objectives |
| `workout_parser.py` | Parses pasted workouts into structured data |
| `database.py` | Local SQLite database layer (used by the app today) |
| `api_client.py` | HTTP client for the online API, with the same functions as `database.py` (not wired into the app yet) |
| `translations.py` | PT/EN texts |

## Roadmap

- [x] PostgreSQL schema and data layer (users, exercises, PRs)
- [x] Flask API with token authentication (register, login, PRs, exercises)
- [x] HTTP client for the app (`api_client.py`), tested against the API
- [ ] API routes for PRs by muscle group and for deleting all PRs of an exercise
- [ ] Login screen in the app
- [ ] Switch the app from local SQLite to the API
- [ ] Host the API
- [ ] Move the workout log (JSON) to the online database
- [ ] Exercise name translation stopped working after the move to a database and needs to be reworked
- [ ] Connect different exercise names (translations) to a single output
- [ ] Add a variety of exercises

## License

All rights reserved. This code is public for viewing and evaluation only. See [LICENSE](LICENSE).