# Northern New Mexico College Student Hub

This site helps Northern New Mexico College students explore NNMC programs,
review official College Scorecard data, and build personalized education plans.

- `fastapi_backend/` — FastAPI service for authentication, NNMC catalog data,
  College Scorecard metrics, education-plan persistence, and scheduling.
- `ChatbotUI/` — React + Vite SPA for the NNMC overview, student profile,
  programs and careers, degree planning, and saved plans.

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL
- College Scorecard API key from https://collegescorecard.ed.gov/data/documentation/

## Backend setup

```bash
cd fastapi_backend
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
alembic upgrade head
uvicorn app.main:app --reload
```

Configure `DATABASE_URL`, `JWT_SECRET`, `COLLEGE_SCORECARD_API_KEY`, and the
other required settings in `fastapi_backend/.env`.

Useful endpoints:

- `GET /api/universities?search=Northern%20New%20Mexico%20College` — NNMC
  enriched with College Scorecard unit ID `188058`.
- `GET /api/universities/{unit_id}` — detailed NNMC metrics.
- `GET /api/programs` — NNMC academic programs only.
- `/api/users/*` — authentication and education-plan endpoints.

## Frontend setup

```bash
cd ChatbotUI
npm install
npm run dev
```

Set `VITE_API_BASE_URL=http://localhost:8000/api` in `ChatbotUI/.env` when the
frontend and backend run separately. The default development URL is
`http://localhost:5173`.

## Verification

```bash
cd ChatbotUI
npm run lint
npm run build

cd ../fastapi_backend
pytest
```
