from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class Station(Base):
    __tablename__ = "stations"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    brand: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    lat: Mapped[float] = mapped_column(Float)
    lng: Mapped[float] = mapped_column(Float)
    street: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    house_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    post_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    prices: Mapped[list[PriceSnapshot]] = relationship("PriceSnapshot", back_populates="station")


class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    station_id: Mapped[str] = mapped_column(ForeignKey("stations.id"))
    captured_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    fuel_type: Mapped[str] = mapped_column(String)
    price_eur: Mapped[float] = mapped_column(Float)

    station: Mapped[Station] = relationship("Station", back_populates="prices")


class WeatherSnapshot(Base):
    __tablename__ = "weather_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    temperature_c: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    humidity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    wind_speed_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    precipitation_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cloud_cover_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


class FeatureVector(Base):
    __tablename__ = "feature_vectors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    target_timestamp: Mapped[datetime] = mapped_column(DateTime)
    fuel_type: Mapped[str] = mapped_column(String)
    current_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    features_json: Mapped[str] = mapped_column(String)  # JSON payload stored as string
    label_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
