from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.core.config import settings
from backend.app.models.base import Base

engine = create_engine(
    settings.nebula_database_url,
    connect_args={"check_same_thread": False} if settings.nebula_database_url.startswith("sqlite") else {},
    echo=settings.nebula_env == "development",
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
