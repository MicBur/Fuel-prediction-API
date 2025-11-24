"""OpenWeatherMap ingest helpers.

Implementation will be completed once API keys are available. For now the module
contains typed skeletons to unblock downstream components."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from loguru import logger

from src.config.settings import get_settings


@dataclass(slots=True)
class WeatherPoint:
    timestamp: datetime
    temperature_c: float
    humidity: Optional[float]
    wind_speed_ms: Optional[float]
    precipitation_mm: Optional[float]
    cloud_cover_pct: Optional[float]


class OpenWeatherClient:
    BASE_URL = "https://api.openweathermap.org/data/3.0"

    def __init__(self, api_key: Optional[str] = None, timeout: float = 10.0) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.openweather_api_key
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)

    def fetch_forecast(self, lat: float, lon: float) -> List[WeatherPoint]:
        if not self.api_key:
            logger.warning("OpenWeather API key missing; returning empty forecast")
            return []

        url = f"{self.BASE_URL}/onecall"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric",
        }
        response = self._client.get(url, params=params)
        response.raise_for_status()
        payload: Dict[str, Any] = response.json()

        forecast: List[WeatherPoint] = []
        for item in payload.get("hourly", []):
            forecast.append(
                WeatherPoint(
                    timestamp=datetime.fromtimestamp(item["dt"]),
                    temperature_c=float(item.get("temp", 0.0)),
                    humidity=item.get("humidity"),
                    wind_speed_ms=item.get("wind_speed"),
                    precipitation_mm=(item.get("rain", {}) or {}).get("1h"),
                    cloud_cover_pct=item.get("clouds"),
                )
            )

        return forecast

    def close(self) -> None:
        self._client.close()


__all__ = ["OpenWeatherClient", "WeatherPoint"]
