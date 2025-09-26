# app/alembic/env.py
from __future__ import annotations
import os, sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool, create_engine

# --- Make 'import app.*' work when Alembic runs from /app/alembic ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import Base, DATABASE_URL  # noqa: E402
from app import models  # noqa: F401,E402  # ensure models are imported for autogenerate

# Alembic Config
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def _db_url() -> str:
    # Prefer env var; fall back to app.database.DATABASE_URL
    return os.environ.get("DATABASE_URL", DATABASE_URL)

def run_migrations_offline() -> None:
    url = _db_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    url = _db_url()
    connectable = create_engine(url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
