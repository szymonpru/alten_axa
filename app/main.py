import logging

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api import users, pokemons
from app.core.logging_config import setup_logging

setup_logging()

logging.info("Starting FastAPI application...")

app = FastAPI()

origins = ["*"]  # TODO add origins to .env

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(pokemons.router)
