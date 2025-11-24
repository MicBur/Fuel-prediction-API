from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # API credentials
    tankerkoenig_api_key: Optional[str] = None
    openweather_api_key: Optional[str] = None
    dwd_api_key: Optional[str] = None

    # Location defaults
    hamburg_lat: float = 53.5511
    hamburg_lng: float = 9.9937
    search_radius_km: float = 5.0
    fuel_type: str = "e5"

    # Paths
    sqlite_path: Path = Path("data/benzin.db")
    model_dir: Path = Path("models")

    # Scheduler settings
    prediction_interval_minutes: int = 5
    retrain_interval_hours: int = 24
    weather_refresh_minutes: int = 10
    price_refresh_minutes: int = 5

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Return cached Settings instance."""

    return Settings()
