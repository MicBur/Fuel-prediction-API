import uvicorn

from src.config.settings import get_settings


def run() -> None:
    settings = get_settings()
    uvicorn.run(
        "src.api.app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
        factory=False,
    )


if __name__ == "__main__":
    run()
