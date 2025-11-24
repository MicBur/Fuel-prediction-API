"""ETL orchestration for fuel + weather data."""
from __future__ import annotations

from datetime import datetime

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.config.settings import get_settings
from src.db import models
from src.db.session import SessionLocal
from src.ingest.tankerkoenig import TankerkoenigClient
from src.ingest.weather_service import WeatherService


class ETLPipeline:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.tk_client = TankerkoenigClient()
        self.weather_service = WeatherService()

    def sync_stations(self, session: Session) -> None:
        stations = self.tk_client.list_stations(
            lat=self.settings.hamburg_lat,
            lng=self.settings.hamburg_lng,
            radius_km=self.settings.search_radius_km,
            fuel_type=self.settings.fuel_type,
        )
        for station in stations:
            existing = session.get(models.Station, station.id)
            if existing:
                existing.name = station.name
                existing.brand = station.brand
                existing.lat = station.lat
                existing.lng = station.lng
                existing.street = station.street
                existing.house_number = station.house_number
                existing.post_code = station.post_code
            else:
                session.add(
                    models.Station(
                        id=station.id,
                        name=station.name,
                        brand=station.brand,
                        lat=station.lat,
                        lng=station.lng,
                        street=station.street,
                        house_number=station.house_number,
                        post_code=station.post_code,
                    )
                )
        session.commit()
        logger.info("Synced %s stations from Tankerkönig", len(stations))

    def capture_prices(self, session: Session) -> None:
        station_ids = [row[0] for row in session.execute(select(models.Station.id)).all()]
        if not station_ids:
            logger.warning("No stations cached yet; skipping price capture")
            return

        for chunk_start in range(0, len(station_ids), 10):
            chunk = station_ids[chunk_start : chunk_start + 10]
            prices = self.tk_client.get_prices(chunk)
            for station_id, payload in prices.items():
                price_value = payload.get(self.settings.fuel_type)
                if price_value is None:
                    continue
                session.add(
                    models.PriceSnapshot(
                        station_id=station_id,
                        fuel_type=self.settings.fuel_type,
                        price_eur=price_value,
                        captured_at=datetime.utcnow(),
                    )
                )
        session.commit()
        logger.info("Captured latest prices for %s stations", len(station_ids))

    def capture_weather(self, session: Session) -> None:
        forecast = self.weather_service.get_forecast()
        for entry in forecast:
            session.add(
                models.WeatherSnapshot(
                    captured_at=entry.timestamp,
                    temperature_c=entry.temperature_c,
                    humidity=entry.humidity,
                    wind_speed_ms=entry.wind_speed_ms,
                    precipitation_mm=entry.precipitation_mm,
                    cloud_cover_pct=entry.cloud_cover_pct,
                )
            )
        session.commit()
        logger.info("Persisted %s weather points", len(forecast))

    def run_all(self) -> None:
        with SessionLocal() as session:
            self.sync_stations(session)
            self.capture_prices(session)
            self.capture_weather(session)


__all__ = ["ETLPipeline"]
