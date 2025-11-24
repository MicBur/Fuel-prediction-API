# Benzin Forecast Service

Fuel price prediction stack for Hamburg that:

- Ingests Tankerkönig pump prices and OpenWeather/DWD signals.
- Stores raw + feature engineered data in SQLite for transparency.
- Trains AutoGluon models daily to capture the relationship between weather and current fuel prices.
- Serves 24h forecasts (5-minute granularity) via FastAPI, backed by APScheduler inside a single Docker container.

## Architecture Overview

```
				+----------------+
				| APScheduler    |
				| (in FastAPI)   |
				+--------+-------+
							|
		  +------------v-------------+
		  | ETL Pipeline             |
		  | Tankerkönig + Weather    |
		  +------------+-------------+
							|
				  SQLite Storage
							|
		  +------------v-------------+
		  | AutoGluon Trainer        |
		  +------------+-------------+
							|
		  +------------v-------------+
		  | FastAPI Prediction Route |
		  +--------------------------+
```

Key components live under `src/`:

- `src/config`: `.env` driven configuration via Pydantic Settings.
- `src/ingest`: Tankerkönig client, weather clients, and ETL orchestration.
- `src/db`: SQLAlchemy models plus schema bootstrap for SQLite.
- `src/models`: AutoGluon training hooks (placeholder until data collection completes).
- `src/api`: FastAPI application with prediction routes and scheduler wiring.

## Getting Started

1. **Install dependencies** (Python 3.11):
	```bash
	pip install -r requirements.txt
	```
2. **Configure environment**:
	```bash
	cp .env.example .env
	# fill in TANKERKOENIG_API_KEY, OPENWEATHER_API_KEY, DWD_API_KEY
	```
3. **Initialize database** (optional while schema evolves):
	```bash
	sqlite3 data/benzin.db < src/db/schema.sql
	```
4. **Run development server**:
	```bash
	python -m src.main
	# FastAPI docs at http://localhost:8000/docs
	```

## Docker

```
docker-compose up --build
```

The container runs FastAPI and APScheduler together, pulling config from `.env`. Mounts the repository so code changes reflect immediately.

## Maintenance Scripts

- `scripts/run_etl_once.py` – manually trigger data ingestion.
- `scripts/retrain.py` – manual AutoGluon retrain hook (daily retraining is scheduled automatically).

## Roadmap

- Wire OpenWeather/DWD fallbacks once API keys are active.
- Implement AutoGluon training + inference pipeline with feature store exports.
- Add observability (structured logging, metrics) and CI workflows for model quality.
