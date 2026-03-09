from __future__ import annotations

"""Database engine, migrations, and session lifecycle helpers."""

import os
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

SERVICE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SERVICE_DIR.parent
load_dotenv(PROJECT_ROOT / ".env", override=False)
load_dotenv(SERVICE_DIR / ".env", override=False)


def build_database_url() -> str:
    """Build SQLAlchemy connection URL from `DATABASE_URL` or PG parts."""
    explicit_url = os.getenv("DATABASE_URL")
    if explicit_url:
        return explicit_url

    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "password")
    db_name = os.getenv("POSTGRES_DB", "customer_db")
    host = os.getenv("POSTGRES_HOST", "postgres")
    port = os.getenv("POSTGRES_PORT", "5432")
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


DATABASE_URL = build_database_url()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy models."""

    pass


def run_migrations() -> None:
    """Execute SQL files in `migrations/` in lexicographical order."""
    migrations_dir = Path(__file__).resolve().parent / "migrations"
    if not migrations_dir.exists():
        return

    migration_files = sorted(migrations_dir.glob("*.sql"))
    if not migration_files:
        return

    with engine.begin() as connection:
        for migration_file in migration_files:
            sql = migration_file.read_text(encoding="utf-8").strip()
            if not sql:
                continue
            connection.execute(text(sql))


def init_db() -> None:
    """Run migrations and ensure model tables exist."""
    run_migrations()
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Yield a request-scoped database session and close it afterwards."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
