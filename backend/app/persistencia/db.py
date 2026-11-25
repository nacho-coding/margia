import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


def database_url() -> str:
    value = os.environ.get("DATABASE_URL")
    if not value or not value.startswith("postgresql+psycopg://"):
        raise RuntimeError("DATABASE_URL debe apuntar a PostgreSQL mediante psycopg.")
    return value


engine = create_engine(database_url(), pool_pre_ping=True, pool_size=5, max_overflow=3,
                       hide_parameters=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_db() -> Generator[Session]:
    with SessionLocal() as session:
        yield session
