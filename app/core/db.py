import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

engine = create_async_engine(get_settings().DB_URI)

# Async session factory
SessionLocal = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


async def get_db():
    """Dependency to provide an async database session for FastAPI endpoints."""
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except (IntegrityError, SQLAlchemyError):
            await session.rollback()
            logger.exception("DB error")
            raise
