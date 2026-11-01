<p align="center">
  <img src="assets/icon.png" width="120" alt="Backbone icon" />
</p>

<h1 align="center">Backbone</h1>

<p align="center">
  A workout tracker for Android and desktop where you just paste your training log and the app does the rest.
</p>

> 🚧 **Status:** in development (v1.13a). Built solo with Python and Flet.

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
- **Online database (in progress):** the PostgreSQL layer (Neon) with users, exercises and PRs is built and tested. The app itself still runs on local SQLite until the API layer is ready

## Workout format

```text
08/28 - your title
bench press
10x 40kg
8x 60kg - F, PR (notes)
```

The first line holds the date and an optional title. Then comes the exercise name, followed by one line per set (`reps x weight`). Tags after the set (`F` for failure, `PR` for personal record) and notes in parentheses are optional.

## Tech stack

- **Python**
- **Flet** (UI, Android and desktop)
- **SQLite3** (local database, used by the app today)
- **PostgreSQL / Neon** (online database)
- **psycopg2**, **bcrypt** and **python-dotenv** (online database access, password hashing and configuration)

## Project structure

| File | Purpose |
|---|---|
| `main.py` | App entry point: UI screens and navigation |
| `core.py` | Core app logic: processing workouts, logging PRs and objectives |
| `workout_parser.py` | Parses pasted workouts into structured data |
| `database.py` | Local SQLite database layer (used by the app, will be removed later) |
| `online_database.py` | PostgreSQL (Neon) database layer: tables, users (bcrypt), exercises and PRs |
| `translations.py` | PT/EN texts |

## Roadmap

- [x] PostgreSQL schema and data layer (users, exercises, PRs)
- [ ] Move the workout log (JSON) to the online database
- [ ] API between the app and the online database
- [ ] Switch the app from local SQLite to the online database
- [ ] Exercise name translation stopped working after the move to a database and needs to be reworked
- [ ] Connect different exercise names (translations) to a single output
- [ ] Add a variety of exercises

## License

All rights reserved. This code is public for viewing and evaluation only. See [LICENSE](LICENSE).