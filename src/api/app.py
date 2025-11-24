from __future__ import annotations

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI

from src.api.routes.predictions import router as predictions_router
from src.config.settings import get_settings
from src.ingest.etl import ETLPipeline
from src.models.train import AutoMLTrainer

app = FastAPI(title="Benzin Forecast API", version="0.1.0")
app.include_router(predictions_router)

settings = get_settings()
scheduler = AsyncIOScheduler()
etl_pipeline = ETLPipeline()
trainer = AutoMLTrainer()


@app.on_event("startup")
async def on_startup() -> None:
    scheduler.add_job(
        etl_pipeline.run_all,
        IntervalTrigger(minutes=settings.price_refresh_minutes),
        id="etl-job",
        replace_existing=True,
    )
    scheduler.add_job(
        trainer.retrain,
        IntervalTrigger(hours=settings.retrain_interval_hours),
        id="retrain-job",
        replace_existing=True,
    )
    scheduler.start()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    scheduler.shutdown(wait=False)
