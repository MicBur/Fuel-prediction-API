from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config.settings import get_settings

_settings = get_settings()
_engine = create_engine(f"sqlite:///{_settings.sqlite_path}", echo=False, future=True)
SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
