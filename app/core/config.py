import logging

from pydantic_settings import BaseSettings
from sqlalchemy import URL


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_DB: str

    LOG_LEVEL: int = logging.INFO  # TODO move it to .env

    @property
    def DB_URI(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.DB_USERNAME,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_DB,
        )

    class Config:
        env_file = ".env"


settings = Settings()
