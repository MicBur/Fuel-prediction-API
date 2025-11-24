"""Historical weather ingestion leveraging Meteostat (DWD-based) datasets."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Optional

from loguru import logger
from meteostat import Hourly, Point
from pandas import isna

from src.config.settings import get_settings
from src.db import models
from src.db.session import SessionLocal


class HistoricalWeatherIngestor:
    def __init__(self, lat: Optional[float] = None, lng: Optional[float] = None) -> None:
        settings = get_settings()
        self.lat = lat or settings.hamburg_lat
        self.lng = lng or settings.hamburg_lng
        self.point = Point(self.lat, self.lng)

    def fetch_hourly(self, start: datetime, end: datetime) -> Hourly:
        """Return Meteostat Hourly dataset for the specified window."""

        start_utc = start.astimezone(timezone.utc)
        end_utc = end.astimezone(timezone.utc)
        return Hourly(self.point, start_utc, end_utc, timezone="UTC")

    def backfill(self, days: int = 7) -> int:
        """Fetch historical data for the last `days` days and persist it."""

        end = datetime.now(timezone.utc)
        start = end - timedelta(days=days)
        dataset = self.fetch_hourly(start, end)
        frame = dataset.fetch()
        if frame.empty:
            logger.warning("No historical weather data returned by Meteostat")
            return 0

        inserted = 0
        with SessionLocal() as session:
            for timestamp, row in frame.iterrows():
                captured_at = timestamp.to_pydatetime().replace(tzinfo=None)
                if self._snapshot_exists(session, captured_at):
                    continue
                snapshot = models.WeatherSnapshot(
                    captured_at=captured_at,
                    temperature_c=self._clean(row.get("temp")),
                    humidity=self._clean(row.get("rhum")),
                    wind_speed_ms=self._derive_wind_speed(row.get("wspd")),
                    precipitation_mm=self._clean(row.get("prcp")),
                    cloud_cover_pct=self._estimate_cloud_cover(row.get("coco")),
                )
                session.add(snapshot)
                inserted += 1
            session.commit()
        logger.info("Inserted %s historical weather rows (days=%s)", inserted, days)
        return inserted

    @staticmethod
    def _snapshot_exists(session, captured_at: datetime) -> bool:
        stmt = (
            session.query(models.WeatherSnapshot.id)
            .filter(models.WeatherSnapshot.captured_at == captured_at)
            .limit(1)
        )
        return session.query(stmt.exists()).scalar()

    @staticmethod
    def _clean(value: Optional[float]) -> Optional[float]:
        if value is None or isna(value):
            return None
        return float(value)

    @staticmethod
    def _derive_wind_speed(speed_kmh: Optional[float]) -> Optional[float]:
        value = HistoricalWeatherIngestor._clean(speed_kmh)
        if value is None:
            return None
        return value / 3.6  # convert km/h to m/s

    @staticmethod
    def _estimate_cloud_cover(code: Optional[float]) -> Optional[float]:
        value = HistoricalWeatherIngestor._clean(code)
        if value is None:
            return None
        normalized = max(0.0, min(1.0, value / 9.0))
        return round(normalized * 100.0, 2)


__all__: List[str] = ["HistoricalWeatherIngestor"]
