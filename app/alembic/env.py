# app/alembic/env.py
from logging.config import fileConfig
import os, sys
from alembic import context
from sqlalchemy import create_engine, pool

# Make 'import app.*' work when running from /app
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

# Alembic Config
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import Base and models so tables register on Base.metadata
from app.database import Base, DATABASE_URL
import app.models  # noqa: F401

target_metadata = Base.metadata

def run_migrations_offline():
    """Only used for --sql; autogenerate won't work here."""
    url = DATABASE_URL or config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Used for real migrations & autogenerate."""
    url = DATABASE_URL or config.get_main_option("sqlalchemy.url")
    connectable = create_engine(url, poolclass=pool.NullPool, future=True)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        print("ALEMBIC ONLINE, tables in metadata:", sorted(target_metadata.tables.keys()))
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
