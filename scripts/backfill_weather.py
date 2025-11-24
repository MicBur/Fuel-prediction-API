"""Run a Meteostat-backed historical weather import."""
import argparse

from src.ingest.weather_history import HistoricalWeatherIngestor


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backfill weather data via Meteostat")
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of trailing days to backfill (default: 30)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ingestor = HistoricalWeatherIngestor()
    inserted = ingestor.backfill(days=args.days)
    print(f"Inserted {inserted} weather rows from the last {args.days} days")


if __name__ == "__main__":
    main()
