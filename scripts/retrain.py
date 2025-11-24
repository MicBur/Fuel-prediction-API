"""Trigger AutoML retraining manually."""
from src.models.train import AutoMLTrainer


def main() -> None:
    AutoMLTrainer().retrain()


if __name__ == "__main__":
    main()
