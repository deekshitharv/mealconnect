# MealConnect

A food sharing and reservation system. Providers list surplus meals, and users browse and reserve portions to collect in person.

## Live links

| What | URL |
|---|---|
| Frontend | https://mealconnect-eight.vercel.app |
| API | https://mealconnect-bq04.onrender.com |
| Swagger docs | https://mealconnect-bq04.onrender.com/docs |

Note: the API runs on a free plan and may take about a minute to wake up on the first request.

## Tech stack

- Backend: FastAPI, SQLAlchemy, Alembic, PostgreSQL (Neon)
- Frontend: React + Vite
- Hosting: Render (API, Docker), Vercel (frontend), Neon (database)

## Roles

- User: browse meals, reserve portions, view reservations
- Provider: create and manage meal listings
- Admin: view statistics, manage users, meals and reservations

## Run locally

With Docker:

    docker compose up --build

Or run the backend and frontend separately:

    cd backend
    uvicorn app.main:app --reload

    cd frontend
    npm install
    npm run dev

## Demo data

Demo accounts and meals are created by `backend/seed.py`. The admin password is set through the `SEED_ADMIN_PASSWORD` environment variable.

## API testing

A Postman collection is included in the `postman` folder, and the interactive docs are at `/docs`.