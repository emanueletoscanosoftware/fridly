from __future__ import annotations

import os, sys
from pathlib import Path
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from dotenv import load_dotenv, find_dotenv

# Path: rende importabile "app" quando si esegue da migrations/
BASE_DIR = Path(__file__).resolve().parents[1]  # .../backend
sys.path.append(str(BASE_DIR))

# Carica .env (prima percorso esplicito, poi fallback)
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True) or load_dotenv(find_dotenv(), override=True)

# Config Alembic e logging
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Imposta URL DB dalla .env
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise RuntimeError(f"DATABASE_URL non trovata (cercato in {ENV_PATH}).")
config.set_main_option("sqlalchemy.url", db_url)

# Metadata dei modelli
from app.db import Base
import app.models  # importa per registrare tutti i modelli
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata,
                      literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
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
