"""DWD (Deutscher Wetterdienst) ingest stubs."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from loguru import logger

from src.config.settings import get_settings


@dataclass(slots=True)
class DWDWeatherRecord:
    timestamp: datetime
    temperature_c: Optional[float]
    humidity: Optional[float]
    wind_speed_ms: Optional[float]
    pressure_hpa: Optional[float]


class DWDClient:
    """Placeholder for the DWD API/file access client."""

    def __init__(self, api_key: Optional[str] = None, cache_dir: Path | None = None) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.dwd_api_key
        self.cache_dir = cache_dir or Path("data/dwd")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def fetch_historical(self, station_id: str) -> List[DWDWeatherRecord]:
        logger.info(
            "DWD historical fetch requested for station {} (not implemented yet)",
            station_id,
        )
        return []


__all__ = ["DWDClient", "DWDWeatherRecord"]
