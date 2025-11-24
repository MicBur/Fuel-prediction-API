"""High-level weather service that wraps OpenWeather + DWD clients."""
from __future__ import annotations

from datetime import datetime
from typing import List

from loguru import logger

from src.config.settings import get_settings
from src.ingest.weather_dwd import DWDClient, DWDWeatherRecord
from src.ingest.weather_openweather import OpenWeatherClient, WeatherPoint


class WeatherService:
    def __init__(self) -> None:
        settings = get_settings()
        self.ow_client = OpenWeatherClient(api_key=settings.openweather_api_key)
        self.dwd_client = DWDClient(api_key=settings.dwd_api_key)

    def get_forecast(self) -> List[WeatherPoint]:
        settings = get_settings()
        forecast = self.ow_client.fetch_forecast(settings.hamburg_lat, settings.hamburg_lng)
        if not forecast:
            logger.warning("OpenWeather forecast empty; downstream logic should handle fallback once available")
        return forecast

    def get_historical(self, station_id: str) -> List[DWDWeatherRecord]:
        return self.dwd_client.fetch_historical(station_id)

    def get_latest_temperature(self) -> float | None:
        forecast = self.get_forecast()
        if not forecast:
            return None
        forecast.sort(key=lambda p: abs((p.timestamp - datetime.utcnow()).total_seconds()))
        return forecast[0].temperature_c


__all__ = ["WeatherService"]
