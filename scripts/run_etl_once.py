"""Utility script to run the ETL pipeline once for debugging."""
from src.ingest.etl import ETLPipeline


def main() -> None:
    ETLPipeline().run_all()


if __name__ == "__main__":
    main()
