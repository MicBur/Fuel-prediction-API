"""Thin client to communicate with the Tankerkönig API.

The implementation follows the public endpoints documented in tanker.md:
- list.php: proximity search returning station metadata and current prices
- prices.php: batch price lookup for up to 10 station UUIDs
- detail.php: extended metadata / opening time details for a single station
- complaint.php: not implemented yet, but method placeholder is provided for future use
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

import httpx
from loguru import logger

from src.config.settings import get_settings


@dataclass(slots=True)
class Station:
    id: str
    name: str
    brand: Optional[str]
    street: Optional[str]
    place: Optional[str]
    lat: float
    lng: float
    dist: Optional[float]
    diesel: Optional[float]
    e5: Optional[float]
    e10: Optional[float]
    is_open: Optional[bool]
    house_number: Optional[str]
    post_code: Optional[int]


class TankerkoenigClient:
    BASE_URL = "https://creativecommons.tankerkoenig.de/json"

    def __init__(self, api_key: Optional[str] = None, timeout: float = 10.0) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.tankerkoenig_api_key
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)

    def _request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if not self.api_key:
            raise RuntimeError("Tankerkönig API key is not configured yet")

        url = f"{self.BASE_URL}/{endpoint}"
        response = self._client.get(url, params={"apikey": self.api_key, **params})
        response.raise_for_status()
        payload = response.json()

        if not payload.get("ok", False):
            message = payload.get("message", "unknown error")
            raise RuntimeError(f"Tankerkönig API call failed: {message}")

        return payload

    def list_stations(
        self,
        lat: float,
        lng: float,
        radius_km: float,
        fuel_type: str,
        sort_by: str = "dist",
    ) -> List[Station]:
        """Return stations within the given radius."""

        logger.debug(
            "Requesting Tankerkönig list: lat={}, lng={}, radius={}, fuel_type={}",
            lat,
            lng,
            radius_km,
            fuel_type,
        )

        payload = self._request(
            "list.php",
            {
                "lat": lat,
                "lng": lng,
                "rad": radius_km,
                "type": fuel_type,
                "sort": sort_by,
            },
        )

        stations: List[Station] = []
        for raw in payload.get("stations", []):
            stations.append(
                Station(
                    id=raw["id"],
                    name=raw.get("name", ""),
                    brand=raw.get("brand"),
                    street=raw.get("street"),
                    place=raw.get("place"),
                    lat=raw["lat"],
                    lng=raw["lng"],
                    dist=raw.get("dist"),
                    diesel=raw.get("diesel"),
                    e5=raw.get("e5"),
                    e10=raw.get("e10"),
                    is_open=raw.get("isOpen"),
                    house_number=raw.get("houseNumber"),
                    post_code=raw.get("postCode"),
                )
            )

        return stations

    def get_prices(self, station_ids: Iterable[str]) -> Dict[str, Any]:
        """Return current prices for up to 10 station UUIDs."""

        joined_ids = ",".join(station_ids)
        if not joined_ids:
            return {}

        payload = self._request("prices.php", {"ids": joined_ids})
        return payload.get("prices", {})

    def get_station_details(self, station_id: str) -> Dict[str, Any]:
        """Return extended metadata for a station."""

        payload = self._request("detail.php", {"id": station_id})
        return payload.get("station", {})

    def close(self) -> None:
        self._client.close()


__all__ = ["TankerkoenigClient", "Station"]
