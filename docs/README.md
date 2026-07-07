# EduPlan Platform

EduPlan helps students discover colleges, compare outcomes, and build
personalized education plans. The repository now contains:

- `fastapi_backend/` – FastAPI service that proxies the U.S. Department of
  Education College Scorecard API, handles authentication, education-plan
  persistence in PostgreSQL, email/SMS utilities, and exposes JSON routes for
  the frontend.
- `ChatbotUI/` – React + Vite SPA with the chatbot, dashboards, college search,
  and plan editors that call the backend.

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 18 (managed on Render/Postgres or any hosted instance)
- College Scorecard API key from https://collegescorecard.ed.gov/data/documentation/

## Backend setup

```bash
cd fastapi_backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .[dev]      # or pip install -r requirements.txt
cp .env.example .env
# edit .env with Postgres creds and COLLEGE_SCORECARD_API_KEY
alembic upgrade head
uvicorn app.main:app --reload
```

Key environment variables (`fastapi_backend/.env`):

- `DATABASE_URL` – use the async Postgres format, e.g.
  `postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DBNAME`.
- `COLLEGE_SCORECARD_API_KEY` – data.gov key required for university endpoints.
- SMTP/Twilio/JWT settings as needed for email, SMS, and auth.

### Useful backend endpoints

- `GET /api/universities?search=mit&state=MA` – live search from College Scorecard.
- `GET /api/universities/{unit_id}` – detailed metrics for a school.
- `POST /api/universities/compare` – pass `{ "unit_ids": ["166027", "130794"] }`.
- `/api/users/*` – auth + education-plan endpoints consumed by the React app.

## Frontend setup

```bash
cd ChatbotUI
npm install
npm run dev   # default: http://localhost:5173
```

- Ensure `ChatbotUI/.env` sets `VITE_API_BASE_URL=http://localhost:8000/api` or
  your deployed backend URL.
- The college finder, chatbot, and program details now read all university data
  from the backend’s College Scorecard proxy; no static JSON files are needed.

## Project structure

```
EdplanCodex/
├── ChatbotUI/                # React SPA
├── fastapi_backend/          # FastAPI service + Alembic migrations
├── README.md                 # this file
└── .vscode/                  # optional IDE helpers
```

## Development workflow

1. Start PostgreSQL locally or point `DATABASE_URL` to an accessible managed instance (e.g., Render Postgres).
2. Run the FastAPI backend (`uvicorn app.main:app --reload`).
3. Run the React frontend (`npm run dev`).
4. Hit `http://localhost:5173` in a browser; the UI will call the backend, which
   relays live College Scorecard data and persists education plans to PostgreSQL.

## Testing & linting

- Backend: `pytest`, `ruff check`, `black --check`.
- Frontend: `npm run lint`.

## Deployment notes

- Set `COLLEGE_SCORECARD_API_KEY` and DB secrets via environment variables or
  secret managers; do not commit them.
- Use `alembic upgrade head` during deployment to keep the PostgreSQL schema in sync.
- Adjust CORS (`CORS_ORIGINS` in backend `.env`) to your production domains.

## Support

If you run into issues bootstrapping either stack, double-check environment
variables, ensure PostgreSQL accepts connections from the backend host, and
confirm your College Scorecard API key is active. Feel free to open Pull
Requests or issues with reproduction steps. Happy building!
