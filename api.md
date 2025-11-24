MicBur/Fuel-Prediction-API – Architecture & API Guide
====================================================

This document mirrors the current GitHub repository https://github.com/MicBur/Fuel-prediction-API.git.
It describes how the FastAPI + AutoGluon stack ingests Tankerkönig and weather data, stores features in
SQLite, retrains daily, and exposes 24h forecasts (5-minute cadence) starting from the latest observed price.

Table of Contents
-----------------

1. Overview
2. Features
3. System Architecture
4. Tech Stack
5. Requirements
6. Local Installation
7. Configuration (.env)
8. Running the API & Scheduler
9. REST Endpoints
10. Data Sources & Pipelines
11. AutoML & Model Lifecycle
12. Error Handling & Logging
13. Testing Strategy
14. Docker & Deployment
15. Chainlink Integration Path
16. Contribution Guide
17. License & Roadmap

1. Overview
-----------

- Scope: Forecast E5 fuel prices for Hamburg, Germany.
- Horizon: 24 hours ahead at 5-minute intervals (288 samples) seeded by the current Tankerkönig price.
- Workflow: Single container runs FastAPI + APScheduler worker. Scheduler triggers ingestion every 5 minutes,
  weather refresh every 15 minutes, and AutoGluon retraining every 24 hours.
- Audience: Energy dashboards, logistics planners, and DeFi/Chainlink oracle consumers.

2. Features
-----------

- Tankerkönig station discovery and batch price polling (list / prices API).
- OpenWeather + DWD ingest skeletons with a weather service façade.
- SQLite-backed historical store (stations, price snapshots, weather snapshots, feature vectors).
- Placeholder AutoGluon retraining hook waiting for accumulated data.
- FastAPI endpoint `/predictions/next24h` returning JSON forecast array.
- Docker + docker-compose definition for reproducible deployments.

3. System Architecture
----------------------

```
┌──────────────────────────┐
│ FastAPI (src/api/app.py) │
│  • REST routes           │
│  • APScheduler jobs      │
└────────────┬─────────────┘
             │
┌────────────v─────────────┐
│ ETL Pipeline             │
│  • Tankerkönig client    │
│  • Weather service       │
│  • SQLite persistence    │
└────────────┬─────────────┘
             │features + labels
┌────────────v─────────────┐
│ AutoGluon Trainer        │
│  • Model artifacts (/models)
│  • Daily retraining      │
└────────────┬─────────────┘
             │predictions
┌────────────v─────────────┐
│ /predictions/next24h API │
└──────────────────────────┘
```

Key modules under `src/`:

- `config/settings.py` – Pydantic Settings reading `.env`.
- `ingest/` – Tankerkönig client, weather clients, ETL coordinator.
- `db/` – SQLAlchemy models + session factory + schema bootstrap.
- `models/train.py` – AutoGluon trainer placeholder, to be expanded with feature engineering.
- `api/` – FastAPI app, routers, dependency wiring.

4. Tech Stack
-------------

- Language: Python 3.11
- Web Framework: FastAPI + Uvicorn
- Scheduling: APScheduler (AsyncIO flavor)
- Data Layer: SQLite (SQLAlchemy ORM)
- AutoML: AutoGluon (planned integration)
- Observability: loguru logging
- Packaging: requirements.txt + pyproject.toml
- Container: Docker (python:3.11-slim base) + docker-compose

5. Requirements
---------------

- Python ≥ 3.11
- pip / venv
- Tankerkönig API key (https://creativecommons.tankerkoenig.de/)
- OpenWeather API key (https://openweathermap.org/api)
- (Optional) DWD credentials or download access, once implemented
- Docker (optional, recommended for deployment)

6. Local Installation
---------------------

```bash
git clone https://github.com/MicBur/Fuel-prediction-API.git
cd Fuel-prediction-API
python -m venv .venv
.venv\Scripts\activate  # Windows (use source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
```

7. Configuration (.env)
-----------------------

Copy `.env.example` → `.env` and set the following variables:

```
TANKERKOENIG_API_KEY=your-key
OPENWEATHER_API_KEY=your-key
DWD_API_KEY=optional
HAMBURG_LAT=53.5511
HAMBURG_LNG=9.9937
SQLITE_PATH=./data/benzin.db
MODEL_DIR=./models
PREDICTION_INTERVAL_MINUTES=5
RETRAIN_INTERVAL_HOURS=24
```

8. Running the API & Scheduler
------------------------------

```bash
python -m src.main
# FastAPI docs at http://localhost:8000/docs
```

The process launches FastAPI, registers APScheduler jobs on startup, and shuts the scheduler down gracefully
on exit. Use `scripts/run_etl_once.py` or `scripts/retrain.py` for manual runs.

9. REST Endpoints
-----------------

- `GET /predictions/next24h`
  - Returns 288 forecast entries (5-minute spacing) for the configured fuel type.
  - Each entry includes ISO timestamp, predicted price (currently placeholder = latest price),
    optional weather metadata, and explanatory notes.
- `GET /docs` / `GET /openapi.json` – auto-generated documentation.

Future endpoints (planned):

- `POST /models/retrain` – manual AutoGluon trigger.
- `GET /health` – service liveness.

10. Data Sources & Pipelines
----------------------------

- **Tankerkönig** – `list.php` for Hamburg stations, `prices.php` for batch quotes. Stored in `stations`
  and `price_snapshots` tables.
- **OpenWeather** – hourly OneCall API for weather projection; persisted to `weather_snapshots`.
- **DWD** – placeholder client (historical backfill to be implemented).

ETL pipeline (`src/ingest/etl.py`) handles:

1. Station synchronization (create/update records).
2. Price capture (chunked polling, respecting 10 IDs/request limit).
3. Weather capture (forecast persistence).

11. AutoML & Model Lifecycle
----------------------------

- Model files stored under `models/` (path configurable via `.env`).
- `AutoMLTrainer.retrain()` currently logs a placeholder; once historical data accumulates, implement:
  - Feature engineering (join price snapshots, weather, calendar features).
  - AutoGluon Tabular training with regression objective.
  - Model versioning and evaluation metrics logging.
- Daily retraining job scheduled by APScheduler using `RETRAIN_INTERVAL_HOURS`.

12. Error Handling & Logging
----------------------------

- HTTP clients (httpx) raise for non-2xx responses; failures bubble up and are logged via loguru.
- Tankerkönig payloads validated by checking `ok == true`; otherwise runtime errors are raised with message context.
- Scheduler jobs should be wrapped with try/except once monitoring hooks are added.

13. Testing Strategy
--------------------

- Add pytest suite under `tests/` (TODO) covering:
  - Tankerkönig client (mocked responses).
  - Weather service fallback logic.
  - ETL state transitions using temporary SQLite DBs.
  - FastAPI routers via `httpx.AsyncClient`.
- Aim for ≥80% coverage using `pytest --cov` once the feature set stabilizes.

14. Docker & Deployment
-----------------------

```bash
docker-compose up --build
```

- `docker/Dockerfile` uses python:3.11-slim, installs requirements, and runs `python -m src.main`.
- Volume mounts keep local code synchronized for iterative development.
- For production, pin dependencies, disable `reload`, and consider multi-stage builds + health checks.
- Windows Task Scheduler (or a container orchestrator) can restart the single container and manage `.env` secrets.

15. Chainlink Integration Path
------------------------------

- Wrap `/predictions/next24h` inside a Chainlink External Adapter to serve DeFi/RWA oracles.
- Adapter responsibilities:
  1. Call API endpoint with desired parameters (fuel type, lat/lng optional when multi-city support exists).
  2. Parse predicted price for target timestamp.
  3. Return JSON payload with `jobRunID`, `data`, and `statusCode` as required by Chainlink nodes.
- Future enhancements: add signed responses, caching, and SLA metrics.

16. Contribution Guide
----------------------

1. Fork → clone → create feature branch (`git checkout -b feat/<topic>`).
2. Ensure black/ruff or preferred linters run clean (add config later).
3. Add/Update tests where applicable.
4. Submit PR with context, screenshots/logs if relevant.
5. Follow semantic/Conventional Commit style (e.g., `feat: add model retrain route`).

17. License & Roadmap
---------------------

- License: MIT (to be added as `LICENSE` file).
- Near-term roadmap:
  - Implement concrete AutoGluon training + prediction logic.
  - Finalize weather fallback (OpenWeather → DWD) and extend beyond Hamburg.
  - Add health checks, auth, and rate limiting for public deployments.
  - Introduce CI (GitHub Actions) for tests + Docker builds.
  - Provide Chainlink adapter template under `adapters/`.

This `api.md` should be committed to the repo (e.g., under `docs/`) to guide contributors and external users.