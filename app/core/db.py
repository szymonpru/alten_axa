import logging

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

engine = create_async_engine(settings.DB_URI)

# Async session factory
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()


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
