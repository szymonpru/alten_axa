import asyncio
import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
import sqlalchemy
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from alembic import command
from alembic.config import Config
from app.core import db
from app.core.config import get_settings
from app.core.security import create_jwt_token
from app.main import app
from app.models import User
from app.tests.factories import BaseFactory


async def run_async_migrations(db_uri: str, db_name: str):
    """Runs Alembic migrations asynchronously by executing them in a subprocess."""
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", f"{db_uri}/{db_name}")

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, command.upgrade, alembic_cfg, "head")


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Setup test database"""
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
    session_patch = pytest.MonkeyPatch()
    session_patch.setenv("DB_DB", test_db_name)
    get_settings.cache_clear()

    new_settings = get_settings()
    new_engine = create_async_engine(new_settings.DB_URI)
    new_sessionmaker = async_sessionmaker(new_engine, expire_on_commit=False)

    # Patch the db module with the new engine and sessionmaker
    session_patch.setattr(db, "engine", new_engine)
    session_patch.setattr(db, "SessionLocal", new_sessionmaker)

    # create app tables in test database
    await run_async_migrations(settings.DB_URI, test_db_name)

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


@pytest_asyncio.fixture(scope="function")
async def session(monkeypatch: pytest.MonkeyPatch) -> AsyncGenerator[AsyncSession]:
    """Create session for tests"""
    connection = await db.engine.connect()
    session = AsyncSession(bind=connection, expire_on_commit=False)

    monkeypatch.setattr(db, "get_db", lambda: session)

    yield session

    await session.close()
    await connection.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_factories(session: AsyncSession) -> AsyncGenerator:
    """
    Automatically set the session for all factories.
    This fixture runs automatically for all tests.
    """
    # Set the session for all factories that inherit from BaseFactory
    BaseFactory.set_session(session)
    yield


@pytest_asyncio.fixture(scope="function")
async def default_user(session: AsyncSession) -> AsyncGenerator[User]:
    """Creates a default user in the test database."""
    user = User(email="test@example.com", hashed_password="hashedpassword")
    session.add(user)
    await session.commit()
    await session.refresh(user)
    yield user

    # Cleanup: Delete the user after the test
    await session.delete(user)
    await session.commit()


@pytest_asyncio.fixture(scope="function")
async def client(default_user) -> AsyncGenerator[AsyncClient]:
    """Client for tests."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as aclient:
        aclient.headers.update(
            {
                "Authorization": f"Bearer {create_jwt_token(default_user.user_id).access_token}"
            }
        )
        yield aclient
