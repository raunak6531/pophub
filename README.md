# PopCulture Hub (Movies + Music + Games)

A Django app that aggregates live data from TMDB (movies/TV), RAWG (games), and Spotify (albums).
User data (ratings, reviews, lists) + API response cache are stored in your database.

## Quick Start (Local)

1) Python 3.11+ recommended.
2) Create a virtualenv and install requirements:

```bash
cd pophub
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3) Create `.env` from the sample and set your keys:

```bash
cp .env.example .env
# edit .env and fill TMDB/RAWG/Spotify keys
```

4) Run migrations:

```bash
python manage.py migrate
python manage.py createsuperuser  # optional
```

5) Start the dev server:

```bash
python manage.py runserver
```

6) Open http://127.0.0.1:8000  and try a search.

## Switch DB to MySQL

Edit `.env` and set DB_ENGINE=mysql and fill DB_* values.
Install MySQL locally and ensure `mysqlclient` builds.

## Endpoints

- `/` – Browse UI (Bootstrap)
- `/api/search?q=tron&type=all|movie|album|game` – unified search
- `/api/item/<type>/<id>` – provider payload + local aggregate rating
- `/api/recs/<type>/<id>` – similar items
- `/api/list/toggle` (POST, login) – add/remove item to a user list
- `/api/rate` (POST, login) – rate + review text

## Notes
- For POST endpoints you must be logged in (Django auth). Use `/admin` to create a user quickly.
- The cache TTL is set via `CACHE_TTL_SECONDS` in `.env`.
