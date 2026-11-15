<p align="center">
  <img src="assets/icon.png" width="120" alt="Backbone icon" />
</p>

<h1 align="center">Backbone</h1>

<p align="center">
  A workout tracker for Android and desktop where you just paste your training log and the app does the rest.
</p>

> 🚧 **Status:** in development (v1.21a). Built solo with Python and Flet.

## Why I built it

I already log my workouts as plain text in my notes, but it was tiring to figure out my next objective for each exercise on the day. Backbone reads that text directly: you paste the workout, and it extracts the exercises, sets, reps and weights, detects personal records, and keeps everything organized.

## Screenshots

<p align="center">
  <img src="images/prs.png" height="400" alt="Your PRs" />
  <img src="images/paste.png" height="400" alt="Paste Workout" />
  <img src="images/goals.png" height="400" alt="Next Objectives" />
</p>

## Features

- **Account:** the app opens on a sign-in screen. Create an account or sign in, and the API keeps your exercises and PRs. If the session expires, Backbone returns to the login screen
- **Paste Workout:** write a workout in free text and the parser extracts exercises, sets, reps and weights
- **Parser feedback:** when a pasted workout can't be fully understood, the app sends the original text and a short reason to the API in the background, so the parser and the exercise list can be improved. It never blocks the app, and if the request fails nothing happens. See [Parser feedback](#parser-feedback) and [Privacy and data](#privacy-and-data)
- **Your PRs:** a personal record for each exercise, detected automatically from your logs and stored on your account
- **Log PR:** add a PR manually
- **Next Objectives:** the next target for each exercise, based on your current PR
- **History:** every logged workout with date and title, expandable and editable. This log still lives on the device
- **Languages:** interface available in Portuguese and English

## Workout format

```text
28/08 - your title
bench press
10x 40kg
8x 60kg - F, PR (notes)
10x 100kg - W
```

The first line holds the date as day/month and an optional title. Then comes the exercise name, followed by one line per set (`reps x weight`). Tags after the set are optional: `F` for failure, `PR` for personal record, and `W` for a warmup set, which is ignored when detecting a PR. Notes in parentheses are optional.

## How the online part works

```
Backbone app (Flet)  →  Backbone API (Flask)  →  PostgreSQL (Neon)
```

The app never talks to the database directly. A database connection string bundled into an Android app could be extracted by anyone, so only the API holds the credentials. The login screen calls the API, receives a signed token, and sends it with each request. The API reads the user from the token, so a user can only see and change their own exercises and PRs.

Accounts, exercises and PRs already go through the hosted API. The pasted workout history is still a local JSON file. The only workout text that reaches the server is what the parser couldn't understand (see below).

The backend lives in its own repository, **`backbone-api`**, which also has the setup instructions (database, `.env` and running the server).

### Parser feedback

```
paste workout → parser → issue check → (only if something is wrong) background POST /parser-failures → parser_failure table
```

After a workout is parsed, `core.find_parser_issues` looks for problems. If the parser rejects the text outright, that is reported too. Each report carries the original text and a reason. Several reasons can be joined with `; ` and the reason is cut at 200 characters.

| Reason | When it happens |
| --- | --- |
| `parse_error: ...` | the parser rejected the text |
| `invalid_date` | the date on the first line isn't a real date (for example `31/02`) |
| `no_exercises` | no exercises and no cardio line were found |
| `unknown_exercise: <name>` | the exercise isn't in the exercise list. A set line the parser couldn't read also ends up here, because it is taken as an exercise name |
| `no_sets: <name>` | an exercise was found but has no sets |

The app side is `send_parser_failure` in `api_client.py`. It runs in a background thread, never raises, ignores any error from the API, and does nothing when there is no session token.

On the server, `POST /parser-failures` requires the token and accepts `raw_text` and `reason`. Both must be non-empty strings without null characters, `raw_text` is limited to 10,000 characters and `reason` to 200 (larger payloads get a `413`). Reports go into the `parser_failure` table (`id`, `user_id`, `raw_text`, `reason`, `date`). `user_id` references `users` with `ON DELETE CASCADE`, so a user's reports disappear with their account.

Unknown exercise names are also a list of what to add next to the exercise list.

### Privacy and data

| Where | What |
| --- | --- |
| On your device | the full workout history (`workouts.json`) |
| On the server | your account, exercises and PRs |
| On the server, only when a workout fails to parse | the text you pasted (including notes in parentheses), the reason, your user id and the time |

Workouts the parser understands are never sent. Parser feedback is linked to your account and removed together with it. Automatic deletion of reports older than 30 days is planned (see the roadmap) but not implemented yet.

## Tech stack

- **Python**
- **Flet** (UI, Android and desktop)
- **requests** (HTTP client the app uses for accounts, exercises, PRs and parser feedback)
- **Flask**, **PostgreSQL / Neon**, **psycopg2**, **bcrypt** (online backend, in `backbone-api`)

## Project structure

| File | Purpose |
|---|---|
| `main.py` | App entry: login first, then the tracker |
| `login.py` | Sign-in and account creation |
| `core.py` | Processing workouts, logging PRs and objectives |
| `workout_parser.py` | Parses pasted workouts into structured data |
| `api_client.py` | HTTP client for the hosted API. This is what the app uses for accounts, exercises and PRs |
| `translations.py` | PT/EN texts |

## Roadmap

- [x] PostgreSQL schema and data layer (users, exercises, PRs)
- [x] Flask API with token authentication (register, login, PRs, exercises)
- [x] HTTP client for the app (`api_client.py`), tested against the API
- [x] API routes for PRs by muscle group and for deleting all PRs of an exercise
- [x] Host the API
- [x] Login screen in the app
- [x] Switch accounts, exercises and PRs from local SQLite to the API
- [x] Report workouts the parser can't understand (`parser_failure` table and `POST /parser-failures`)
- [ ] Privacy notice on the sign-up screen
- [ ] Limit how many parser reports one user can send per day
- [ ] Move the workout log (JSON) to the online database
- [ ] Exercise name translation stopped working after the move to a database and needs to be reworked
- [ ] Connect different exercise names (translations) to a single output
- [ ] Add a variety of exercises

## License

All rights reserved. This code is public for viewing and evaluation only. See [LICENSE](LICENSE).