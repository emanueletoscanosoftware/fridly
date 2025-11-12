from __future__ import annotations

import os
import sys
from pathlib import Path
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# === Path setup: aggiunge la cartella "backend" al PYTHONPATH ===
BASE_DIR = Path(__file__).resolve().parents[1]  # .../backend
sys.path.append(str(BASE_DIR))

# === Carica le variabili da .env (in .../backend/.env) ===
from dotenv import load_dotenv  # type: ignore

ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)

# === Config Alembic (.ini) e logging ===
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# === DATABASE_URL dalla .env ===
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise RuntimeError(
        f"DATABASE_URL non trovata. Crea un file .env in {BASE_DIR} con, ad esempio:\n"
        "DATABASE_URL=postgresql+psycopg://fridly:fridly@localhost:5432/fridly"
    )
config.set_main_option("sqlalchemy.url", db_url)

# === Metadata dei modelli ===
from app.db import Base  # noqa: E402
import app.models  # noqa: F401,E402  # registra tutti i modelli

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Esegue le migrazioni in modalità 'offline'."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Esegue le migrazioni in modalità 'online'."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section) or {},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
