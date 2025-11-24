from __future__ import annotations

from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends

from src.config.settings import Settings, get_settings
from src.ingest.tankerkoenig import TankerkoenigClient
from src.ingest.weather_service import WeatherService

router = APIRouter(prefix="/predictions", tags=["predictions"])


def get_clients():
    return {
        "tk_client": TankerkoenigClient(),
        "weather_service": WeatherService(),
    }


@router.get("/next24h")
def get_predictions(
    settings: Settings = Depends(get_settings),
    clients: dict = Depends(get_clients),
) -> List[dict]:
    """Return placeholder predictions until AutoML is wired in."""

    tk_client: TankerkoenigClient = clients["tk_client"]
    weather_service: WeatherService = clients["weather_service"]

    stations = tk_client.list_stations(
        lat=settings.hamburg_lat,
        lng=settings.hamburg_lng,
        radius_km=settings.search_radius_km,
        fuel_type=settings.fuel_type,
    )
    current_station = stations[0] if stations else None
    current_price = getattr(current_station, settings.fuel_type, None)

    weather_forecast = weather_service.get_forecast()
    start_time = datetime.utcnow()
    interval = timedelta(minutes=settings.prediction_interval_minutes)
    horizon_steps = int(24 * 60 / settings.prediction_interval_minutes)

    predictions: List[dict] = []
    for step in range(horizon_steps):
        ts = start_time + interval * step
        forecast_temp = weather_forecast[step].temperature_c if step < len(weather_forecast) else None
        predictions.append(
            {
                "timestamp": ts.isoformat(),
                "predicted_price": current_price,
                "temperature_c": forecast_temp,
                "notes": "AutoML model pending; returning current price as placeholder",
            }
        )

    return predictions
