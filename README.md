# UptimeWatch

A website uptime monitor. Add a URL, and a background scheduler checks it on an interval, records
response time, and sends an alert when the site goes down or recovers.

**Stack:** React + Tailwind CSS (Vite) · Python FastAPI · SQLAlchemy (SQLite) · APScheduler · JWT auth ·
Docker · GitHub Actions

## Features
- Register / log in (JWT, bcrypt-hashed passwords)
- Add, pause, resume and delete monitors (30 s – 1 h intervals)
- Background scheduler checks due monitors in parallel (thread pool)
- Down detection after N consecutive failures (no false alarms), alert on state change (log, or email via SMTP)
- Dashboard: live status, 24h uptime %, response-time chart, check history, "Check now"
- Daily cron job that deletes old check history
- Security: users only see their own monitors, SSRF protection (private/internal URLs blocked)
- 9 automated tests, Dockerfiles, docker-compose, CI pipeline

## Run locally (without Docker)

You need Python 3.10+ and Node.js 18+.

**Terminal 1 – backend**
```
cd backend
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API docs: http://localhost:8000/docs

**Terminal 2 – frontend**
```
cd frontend
npm install
npm run dev
```
Open http://localhost:5173, sign up, and add a monitor such as `https://google.com`.

> To test "down" detection on your own machine (e.g. `http://localhost:3000`), start the backend with
> private URLs allowed. Windows: `set ALLOW_PRIVATE_URLS=1` then `uvicorn app.main:app --reload`.
> Mac/Linux: `ALLOW_PRIVATE_URLS=1 uvicorn app.main:app --reload`.

## Run with Docker
```
docker compose up --build
```
Open http://localhost:8080

## Run the tests
```
cd backend
pytest
```

## Configuration (environment variables)
| Variable | Default | Meaning |
|---|---|---|
| `SECRET_KEY` | dev value | JWT signing key – **change in production** |
| `DATABASE_URL` | `sqlite:///./uptimewatch.db` | Any SQLAlchemy URL (e.g. PostgreSQL) |
| `TICK_SECONDS` | 15 | How often the scheduler looks for due monitors |
| `FAILURE_THRESHOLD` | 2 | Consecutive failures before a monitor is "down" |
| `RETENTION_DAYS` | 7 | How long check history is kept |
| `ALLOW_PRIVATE_URLS` | 0 | Allow monitoring localhost / private IPs |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` | empty | Enable email alerts |

## Project structure
```
backend/app/
  main.py        app setup, CORS, scheduler lifecycle
  models.py      User, Monitor, CheckResult tables
  schemas.py     request/response validation (Pydantic)
  auth.py        password hashing + JWT
  checker.py     HTTP check, URL validation, state-change logic
  scheduler.py   APScheduler jobs (interval tick + daily cron prune)
  alerts.py      email / log alerts
  routers/       auth.py, monitors.py (REST endpoints)
backend/tests/   pytest tests
frontend/src/
  api/           fetch wrapper with JWT
  context/       AuthContext
  hooks/         useMonitors (polling)
  components/    Navbar, AuthForm, MonitorForm, MonitorCard, SummaryBar, ResponseChart, StatusBadge
  pages/         AuthPage, DashboardPage
```

## API
| Method | Path | Description |
|---|---|---|
| POST | `/api/auth/register`, `/api/auth/login` | Returns a JWT |
| GET | `/api/auth/me` | Current user |
| GET / POST | `/api/monitors` | List / create |
| PATCH / DELETE | `/api/monitors/{id}` | Update (name, interval, pause) / delete |
| GET | `/api/monitors/{id}/results` | Check history |
| POST | `/api/monitors/{id}/check` | Run a check now |

## Resume entry (edit to match what you actually built and can explain)

**UptimeWatch — Website Uptime Monitoring Platform** | React, Tailwind CSS, Python, FastAPI, SQLAlchemy, Docker | Live Demo | GitHub
- Built a full-stack uptime monitor with a React + Tailwind dashboard and a FastAPI REST backend with JWT authentication.
- Implemented a background scheduler (APScheduler) that checks monitors in parallel, records response times, and sends alerts on status changes after consecutive failures to avoid false alarms.
- Added a daily cron cleanup job, SSRF protection for user-supplied URLs, and 9 pytest tests.
- Containerised with Docker (docker-compose), added a GitHub Actions CI pipeline, and deployed on AWS EC2.

(Only write "deployed on AWS EC2" after you actually deploy it.)

## Interview questions you should be ready for
1. **Why a background scheduler instead of checking when the user opens the page?** Monitoring must run 24/7 even when nobody is logged in.
2. **Why does `tick` run every 15 s instead of one job per monitor?** One cheap loop that picks due monitors is simpler and survives restarts, because the state lives in the database.
3. **Why wait for 2 failures before alerting?** One failed request can be a network blip; this avoids false alarms.
4. **What is SSRF and how did you handle it?** The server makes requests to user-supplied URLs, so an attacker could probe internal services. `validate_url` allows only http(s) and public IPs.
5. **Why does each worker thread open its own DB session?** SQLAlchemy sessions are not thread-safe.
6. **What breaks if you run 4 uvicorn workers?** Each would start its own scheduler and every check would run 4 times. Fix: run the scheduler as a separate process, or use a lock / Celery + Redis.
7. **How would you scale this?** PostgreSQL instead of SQLite, a separate worker service, a message queue, and metrics aggregation tables.

## Ideas to extend it (each makes a good talking point)
- Switch to PostgreSQL in docker-compose
- Webhook / Slack alerts
- Public status page per user
- Deploy to AWS EC2 or GCP Cloud Run with the CI pipeline pushing the image
