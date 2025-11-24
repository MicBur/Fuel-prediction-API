# Fuel-Prediction-API

[![Status](https://img.shields.io/badge/status-alpha-blue)](#)
[![Python](https://img.shields.io/badge/python-3.11+-yellow)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.114-brightgreen)](#)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](#)

> FastAPI + AutoGluon stack that ingests Tankerkönig pump prices and weather signals for Hamburg, stores
> everything in SQLite, retrains daily, and serves 24h fuel price forecasts in 5-minute steps.

---

## Table of Contents

1. [Overview](#overview)
2. [Feature Highlights](#feature-highlights)
3. [System Architecture](#system-architecture)
4. [Tech Stack](#tech-stack)
5. [Configuration (.env)](#configuration-env)
6. [Local Quick Start](#local-quick-start)
7. [Scheduler Jobs](#scheduler-jobs)
8. [REST Endpoints](#rest-endpoints)
9. [Data Pipeline](#data-pipeline)
10. [AutoML Lifecycle](#automl-lifecycle)
11. [Docker & Deployment](#docker--deployment)
12. [Maintenance Scripts](#maintenance-scripts)
13. [Chainlink Integration Path](#chainlink-integration-path)
14. [Roadmap](#roadmap)
15. [Contributing](#contributing)

---

## Overview

- **Scope**: Forecast E5 (extendable) fuel prices for Hamburg, Germany.
- **Horizon**: 24 hours → 288 predictions (5-minute cadence) seeded with the *current* Tankerkönig price.
- **Runtime**: Single container hosting FastAPI + APScheduler worker.
- **Goal**: Feed dashboards, logistics tooling, or Chainlink oracles with weather-aware price projections.

## Feature Highlights

- ✅ Tankerkönig proximity and price polling (list/prices endpoints, station cache).
- ✅ Weather ingest façade (OpenWeather live, DWD placeholder for historical backfill).
- ✅ SQLite data store (`stations`, `price_snapshots`, `weather_snapshots`, `feature_vectors`).
- ✅ FastAPI route `/predictions/next24h` returning JSON array of forecast points.
- ✅ Docker + docker-compose setup for painless deployments.
- 🚧 AutoGluon feature engineering + model training (hooks in place, waiting for data).

## System Architecture

```
┌──────────────────────────────┐
│    APScheduler (in FastAPI)  │
│  • price/weather polling     │
│  • daily retraining          │
└──────────────┬───────────────┘
               │
┌──────────────v───────────────┐
│      ETL Pipeline            │
│  • Tankerkönig client        │
│  • Weather service           │
│  • SQLite persistence        │
└──────────────┬───────────────┘
               │ features/labels
┌──────────────v───────────────┐
│     AutoGluon Trainer        │
│  • model dir: /models        │
│  • retrain every 24h         │
└──────────────┬───────────────┘
               │ predictions
┌──────────────v───────────────┐
│ FastAPI `/predictions/next24h│
└──────────────────────────────┘
```

Directory map:

- `src/config` – `.env`-driven settings via Pydantic.
- `src/ingest` – Tankerkönig client, weather clients, ETL orchestration.
- `src/db` – SQLAlchemy models + schema bootstrap.
- `src/models` – AutoGluon trainer placeholder (feature store hooks coming soon).
- `src/api` – FastAPI app, routers, scheduler wiring.

## Tech Stack

| Layer            | Choice                         |
|------------------|--------------------------------|
| Language         | Python 3.11                    |
| Web Framework    | FastAPI + Uvicorn              |
| Scheduler        | APScheduler (AsyncIO)          |
| Data Store       | SQLite (SQLAlchemy ORM)        |
| ML/AutoML        | AutoGluon (planned)            |
| HTTP Clients     | httpx + requests               |
| Logging          | loguru                         |
| Containerization | Docker (python:3.11-slim base) |

## Configuration (.env)

```ini
TANKERKOENIG_API_KEY=xxxx
OPENWEATHER_API_KEY=xxxx
DWD_API_KEY=
HAMBURG_LAT=53.5511
HAMBURG_LNG=9.9937
SQLITE_PATH=./data/benzin.db
MODEL_DIR=./models
PREDICTION_INTERVAL_MINUTES=5
RETRAIN_INTERVAL_HOURS=24
WEATHER_REFRESH_MINUTES=15
PRICE_REFRESH_MINUTES=5
API_HOST=0.0.0.0
API_PORT=8000
```

Copy `.env.example` → `.env` and fill in the keys when they become available.

## Local Quick Start

```bash
git clone https://github.com/MicBur/Fuel-prediction-API.git
cd Fuel-prediction-API
python -m venv .venv
.venv\Scripts\activate  # or source .venv/bin/activate
pip install -r requirements.txt
sqlite3 data/benzin.db < src/db/schema.sql  # optional bootstrap
python -m src.main
# Swagger UI: http://localhost:8000/docs
```

## Scheduler Jobs

| Job ID        | Interval (default) | Action                                  |
|---------------|--------------------|-----------------------------------------|
| `etl-job`     | 5 min              | Sync stations, capture prices, persist weather |
| `weather-job` | 15 min             | (future) dedicated weather refresh      |
| `retrain-job` | 24 h               | AutoGluon retraining hook               |

Intervals can be tuned via `.env`.

## REST Endpoints

- `GET /predictions/next24h`
  - Returns 288 entries: timestamp, predicted_price (currently last observed price), temperature, notes.
  - Future: include confidence intervals + station metadata.
- `GET /docs` / `GET /openapi.json`
  - Interactive schema courtesy of FastAPI.

Planned additions: `GET /health`, `POST /models/retrain`, parameterized prediction routes.

## Data Pipeline

1. **Station Sync** – `list.php` call caches Hamburg stations in `stations` table.
2. **Price Snapshots** – `prices.php` polled in chunks (10 IDs/request) feeding `price_snapshots`.
3. **Weather Snapshots** – OpenWeather hourly forecast stored in `weather_snapshots`; DWD client ready for backfill.
4. **Feature Store** – `feature_vectors` table aggregates engineered features (placeholder until AutoML wiring).

## AutoML Lifecycle

- `AutoMLTrainer.retrain()` (in `src/models/train.py`) prepares model directory and logs invocation.
- Upcoming work:
  1. Build feature joins (price history + weather + calendar/time features).
  2. Train AutoGluon Tabular model, save artifacts in `/models`.
  3. Load best model for inference inside `/predictions/next24h`.
  4. Track metrics and version models for rollback.

## Docker & Deployment

```bash
docker-compose up --build
```

- Uses `docker/Dockerfile` (python:3.11-slim) → installs `requirements.txt` → runs `python -m src.main`.
- Container bundles FastAPI server *and* APScheduler worker to keep things in sync.
- Windows Task Scheduler (or any orchestrator) can restart the container, rotate `.env`, and ship logs.

## Maintenance Scripts

- `scripts/run_etl_once.py` – manual ingestion cycle for debugging.
- `scripts/retrain.py` – manual AutoGluon retraining trigger (same as daily job).

## Chainlink Integration Path

1. Wrap `/predictions/next24h` inside a Chainlink External Adapter.
2. Adapter reads the JSON response, selects the desired timestamp/value, and emits Chainlink-compliant payloads.
3. Future enhancements: signed responses, parameterized fuel types/locations, caching, SLA metrics.

## Roadmap

- [ ] Wire OpenWeather ↔ DWD fallback logic + historical backfill.
- [ ] Implement AutoGluon training + inference pipeline with versioned artifacts.
- [ ] Add health, metrics, and optional auth/rate-limiting middleware.
- [ ] Provide CI (GitHub Actions) for lint/test/build.
- [ ] Publish Chainlink adapter template + docs.

## Contributing

1. Fork → clone → `git checkout -b feat/<topic>`.
2. Keep commits focused; follow Conventional Commit style (`feat:`, `fix:`, `docs:` …).
3. Add/adjust tests (pytest) once suites land.
4. Open PR with description, screenshots/logs where helpful.

---

Need more context? See `api.md` for an extended architecture + API guide.
