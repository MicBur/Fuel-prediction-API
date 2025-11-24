"""AutoGluon training placeholders."""
from __future__ import annotations

from pathlib import Path

from loguru import logger

from src.config.settings import get_settings


class AutoMLTrainer:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.model_dir = Path(self.settings.model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)

    def retrain(self) -> None:
        logger.info("AutoGluon retraining placeholder invoked; implement once data is ready")


__all__ = ["AutoMLTrainer"]
