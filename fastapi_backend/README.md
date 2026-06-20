# EdPlan FastAPI Backend

This service replaces the legacy ASP.NET Core API. It exposes the same routes the React
frontend expects via FastAPI and persists data in PostgreSQL using SQLAlchemy.

## Features

- JWT authentication with password hashing via `passlib`.
- Education plan CRUD, course scheduling, reschedule workflows.
- Customer, dashboard, and global lookup APIs.
- Email and SMS notifications powered by SMTP and Twilio.
- Alembic migrations for schema management.

## Getting Started

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\\Scripts\\activate on Windows
pip install -e .[dev]
cp .env.example .env
uvicorn app.main:app --reload
```

Set `DATABASE_URL` to an async Postgres connection string (PostgreSQL 18), e.g.
```
DATABASE_URL="postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DBNAME"
```

Provide your College Scorecard API key via `COLLEGE_SCORECARD_API_KEY` (see
https://collegescorecard.ed.gov/data/documentation/) so the backend can proxy
all university lookups.

Run migrations after configuring the DB:

```bash
alembic upgrade head
```

See `.env.example` for the full list of required settings.

## Deploying to Render

- Create a managed Postgres instance in Render and copy the connection string.
- Create a Web Service from this repo, set `DATABASE_URL` to the Postgres async URL (`postgresql+asyncpg://...`) and add secrets (`JWT_SECRET`, `COLLEGE_SCORECARD_API_KEY`, SMTP/Twilio, etc.).
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port 10000`.
- Run `alembic upgrade head` on deploy to migrate the schema.
- Configure `CORS_ORIGINS` to your frontend domains.
