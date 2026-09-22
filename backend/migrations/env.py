from alembic import context
from sqlalchemy import engine_from_config, pool

from app.models import Base

config = context.config
config.set_main_option("sqlalchemy.url", config.get_main_option("sqlalchemy.url").replace("+asyncpg", ""))

def run_migrations_online():
    connectable = engine_from_config(config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata)
        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
