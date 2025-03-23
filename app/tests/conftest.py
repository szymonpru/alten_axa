import uuid

import pytest
import pytest_asyncio
import sqlalchemy
from sqlalchemy.ext.asyncio import (
    create_async_engine,
)

from app.core.config import get_settings
from app.models import Base


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    # Create test_db_name
    test_db_name = f"test_db_{str(uuid.uuid4()).replace('-', '_')}"

    # Create admin connection to the DB with isolation_level autocommit. It's important
    settings = get_settings()
    admin_engine = create_async_engine(settings.DB_URI, isolation_level="AUTOCOMMIT")

    # Create test database
    async with admin_engine.connect() as conn:
        await conn.execute(sqlalchemy.text(f"DROP DATABASE IF EXISTS {test_db_name}"))
        await conn.execute(sqlalchemy.text(f"CREATE DATABASE {test_db_name}"))

    # Patch envs
    patch = pytest.MonkeyPatch()
    patch.setenv("DB_DB", test_db_name)

    # Clear cache
    get_settings.cache_clear()

    # Import engine. It will use newly created DB.
    from app.core.db import engine

    # create app tables in test database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Let the tests run
    yield

    # Clean up after all tests have run
    async with admin_engine.connect() as conn:
        # Terminate all active connections to the test database
        await conn.execute(
            sqlalchemy.text(
                f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{test_db_name}'
                AND pid <> pg_backend_pid()
                """
            )
        )
        # Drop the test database
        await conn.execute(sqlalchemy.text(f"DROP DATABASE IF EXISTS {test_db_name}"))

    # Properly dispose engines
    await admin_engine.dispose()
    await engine.dispose()
